import datetime

class Engine:
    def __init__(self, name: str, manufacturer: str, description: str, 
                 cylinders: int, displacement: int, cylinder_bore: float, 
                 piston_stroke: float, compression_ratio: float, 
                 max_rpm: int, max_horsepower: int, max_kw: int, 
                 max_torque_nm: int, ron: int, ecs: str, 
                 peak_torque_rpm: int, peak_hp_rpm: int, clutch_response_time):
        # Visual Info & Trivia
        self.name: str = name
        self.manufacturer: str = manufacturer
        self.description: str = description

        # Specs
        self.cylinders: int = cylinders
        self.displacement: int = displacement
        self.cylinder_bore: float = cylinder_bore
        self.piston_stroke: float = piston_stroke
        self.compression_ratio: float = compression_ratio
        self.max_rpm: int = max_rpm
        self.max_horsepower: int = max_horsepower
        self.max_kw: int = max_kw
        self.max_torque_nm: int = max_torque_nm
        self.RON: int = ron
        self.ECS: str = ecs
        self.peak_torque_rpm: int = peak_torque_rpm  # RPM where peak torque occurs
        self.peak_hp_rpm: int = peak_hp_rpm  # RPM where peak horsepower occurs
        self.clutch_response_time: int = clutch_response_time # Clutch response time in ms

        # Simulation Data
        self.current_hp: float = 0.0
        self.current_torque_nm: float = 0.0
        self.current_rpm: int = 700  # Set idle RPM
        self.throttle: float = 0.0
        self.throttle_decay_rate: float = 0.02  # Throttle decay rate when not accelerating
        self.increase_rate: float = 0  # Rate of RPM increase based on throttle position
        self.base_increase_rate: float = 0.03
        self.current_gear_ratio: float = None
        self.clutched: bool = False # Engine can only generate power to the gearbox if clutch is False
        self.clutched_timestamp: datetime = None

    def calculate_increase_rate(self, gear_ratio: float):
        """
        Calculate the increase rate based on the gear ratio. A smaller gear ratio
        results in a lower increase rate, while a larger gear ratio results in a higher
        increase rate. The increase rate is calculated as the product of the base
        increase rate and the gear ratio.

        Args:
            gear_ratio (float): The gear ratio, where a larger number corresponds to a higher
                                increase rate and a smaller number corresponds to a lower
                                increase rate.
        """
        self.current_gear_ratio = gear_ratio
        self.increase_rate = self.base_increase_rate * gear_ratio / 2

    def update_rpm(self):
        """
        Updates the current RPM based on the throttle input.
        Simulates a more realistic non-linear increase and decrease in RPM,
        including slower increases near maximum RPM, and considering gear ratios.
        
        Args:
            gear_ratio (float): The current gear ratio which affects RPM increase. Higher gear ratios
                                (lower gears) allow faster RPM increases, while lower gear ratios 
                                (higher gears) make it harder to reach max RPM.
        """
        if self.clutched is True:
            self.throttle = 0.0
            if self.clutched_timestamp is None:
                self.clutched_timestamp = datetime.datetime.now()
            else:
                # Check if the difference between now and clutched_timestamp is greater than 1 second
                if datetime.datetime.now() - self.clutched_timestamp > datetime.timedelta(milliseconds=self.clutch_response_time):
                    self.clutched = False
                    self.clutched_timestamp = None
        
        # Calculate the target RPM based on throttle and gear ratio
        target_rpm = int(self.max_rpm * self.throttle * self.current_gear_ratio)
        
        if target_rpm > self.current_rpm:
            # Simulate RPM increase with a non-linear approach
            if self.current_rpm < target_rpm:
                # Gradual increase to target RPM
                increase_rate = (target_rpm - self.current_rpm) * self.increase_rate
                
                # Slow down RPM increase as it approaches the max RPM using a decay factor
                decay_factor = 1 - ((self.current_rpm / self.max_rpm) ** 2)
                self.current_rpm += increase_rate * decay_factor
                
                if self.current_rpm > target_rpm:
                    self.current_rpm = target_rpm
        else:
            # Simulate RPM decay when throttle is released
            if self.current_rpm > 700:
                if self.clutched == False:
                    decay_rate = float(self.current_rpm - target_rpm) * self.increase_rate / 10 # Fixed rate for RPM decay
                elif self.clutched == True:
                    decay_rate = float(self.current_rpm - target_rpm) * self.increase_rate # Fixed rate for RPM decay
                self.current_rpm -= decay_rate
                if self.current_rpm < 700:
                    self.current_rpm = 700

        # Ensure RPM doesn't exceed maximum
        if self.current_rpm > self.max_rpm:
            self.current_rpm = self.max_rpm

        # Update HP and Torque
        self.calculate_current_torque()
        self.calculate_current_hp()

    def calculate_current_hp(self) -> float:
        """
        Calculates the current horsepower (HP) of the engine based on 
        the current torque (in Nm) and the current RPM.
        
        :return: The calculated horsepower (HP) value.
        """
        if self.current_rpm == 0:
            return 0.0

        # Convert torque from Nm to ft-lb
        current_torque_ft_lb = self.current_torque_nm * 0.737562

        # Correct formula to calculate HP using RPM and torque in ft-lb
        self.current_hp = (current_torque_ft_lb * self.current_rpm) / 5252

        # Clamp HP to not exceed max horsepower, if necessary
        if self.current_hp > self.max_horsepower:
            self.current_hp = self.max_horsepower

        return self.current_hp

    def calculate_current_torque(self) -> float:
        """
        Calculates the current torque (Nm) of the engine based on 
        the current RPM, using a more realistic torque curve that
        peaks at a specific RPM and tapers off after.
        
        :return: The calculated torque (Nm) value.
        """
        if self.current_rpm == 0:
            return 0.0

        if self.current_rpm <= self.peak_torque_rpm:
            # Torque increases until peak torque RPM
            self.current_torque_nm = self.max_torque_nm * (self.current_rpm / self.peak_torque_rpm)
        else:
            # Torque decreases more gradually after peak torque RPM
            rpm_range = self.max_rpm - self.peak_torque_rpm
            rpm_post_peak = self.current_rpm - self.peak_torque_rpm
            decrease_factor = 1 - (rpm_post_peak / rpm_range) ** 2
            self.current_torque_nm = self.max_torque_nm * decrease_factor

        # Prevent torque from dropping below 30% of max torque
        min_torque = self.max_torque_nm * 0.3
        self.current_torque_nm = max(self.current_torque_nm, min_torque)

        return self.current_torque_nm
