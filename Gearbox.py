class Gearbox:
    def __init__(self, gear_ratios: list, tire_size: str, final_drive_ratio: float):
        """
        Initializes the Gearbox with gear ratios and tire size.

        :param gear_ratios: List of gear ratios, where the index corresponds to the gear number.
        :param tire_size: The tire size in the format 'Width/AspectRatioRDiameter', e.g., '195/50R16'.
        :param final_drive_ratio: The final drive ratio of the gearbox.
        """
        self.gear_ratios = gear_ratios
        self.current_gear = 1
        self.tire_radius_meters = self.get_wheel_radius(tire_size)
        self.final_drive_ratio = final_drive_ratio

    def shift_up(self):
        """
        Shifts the gearbox up one gear, if not already in the highest gear.
        """
        if self.current_gear < len(self.gear_ratios):
            self.current_gear += 1

    def shift_down(self):
        """
        Shifts the gearbox down one gear, if not already in the lowest gear.
        """
        if self.current_gear > 1:
            self.current_gear -= 1

    def get_current_ratio(self) -> float:
        return self.gear_ratios[self.current_gear - 1]

    def get_wheel_radius(self, tire_size: str) -> float:
        """
        Calculates the wheel radius in meters from a given tire size.

        Args:
            tire_size (str): The tire size in the format 'Width/AspectRatioRDiameter', 
                            e.g., '195/50R16'.

        Returns:
            float: The wheel radius in meters.

        Raises:
            ValueError: If the tire size format is invalid or if the values are not convertible to integers.
        """
        try:
            # Split the tire size string into its components
            width_str, aspect_ratio_and_diameter = tire_size.split('/')
            aspect_ratio_str, diameter_str = aspect_ratio_and_diameter.split('R')
            
            # Convert the string components to integers
            width = int(width_str)
            aspect_ratio = int(aspect_ratio_str)
            diameter = int(diameter_str)
            
            # Calculate the sidewall height in millimeters
            sidewall_height_mm = (width * aspect_ratio) / 100
            
            # Convert sidewall height to meters
            sidewall_height_m = sidewall_height_mm / 1000
            
            # Calculate the wheel radius in meters
            wheel_radius_m = (diameter * 25.4 / 2) / 1000
            
            return wheel_radius_m
        
        except (ValueError, IndexError) as e:
            raise ValueError("Invalid tire size format. Ensure it is in 'Width/AspectRatioRDiameter' format.") from e

    def get_speed(self, engine_rpm: int) -> float:
        """
        Calculates the approximate speed in km/h based on the engine RPM and current gear.

        :param engine_rpm: The current RPM of the engine.
        :return: The approximate speed in km/h.
        """
        gear_ratio = self.gear_ratios[self.current_gear - 1]
        
        # Calculate the speed in km/h
        speed_kph = (engine_rpm * self.tire_radius_meters * 2 * 3.14159 * 60) / (self.final_drive_ratio * gear_ratio * 1000)
        
        return speed_kph
