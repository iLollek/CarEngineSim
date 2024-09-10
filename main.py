import pygame
import pygame.freetype  # For better font rendering
from Engine import Engine
from Gearbox import Gearbox
import math

def draw_slider(screen, x, y, width, height, value):
    """
    Draws a slider on the screen.
    
    :param screen: The Pygame screen to draw on.
    :param x: The x coordinate of the slider.
    :param y: The y coordinate of the slider.
    :param width: The width of the slider.
    :param height: The height of the slider.
    :param value: The current value of the slider (0.0 to 1.0).
    """
    # Draw the slider background
    pygame.draw.rect(screen, (200, 200, 200), (x, y, width, height))
    
    # Draw the slider bar
    slider_pos = int(x + value * width)
    pygame.draw.rect(screen, (0, 150, 0), (x, y, slider_pos - x, height))
    
    # Draw the slider knob
    pygame.draw.circle(screen, (0, 100, 0), (slider_pos, y + height // 2), height // 2)

def draw_rpm_gauge(screen, center_x, center_y, radius, rpm, max_rpm):
    """
    Draws a sleek, modern circular RPM gauge with a needle and redline.

    :param screen: The Pygame screen to draw on.
    :param center_x: The x coordinate of the gauge center.
    :param center_y: The y coordinate of the gauge center.
    :param radius: The radius of the gauge.
    :param rpm: The current RPM value.
    :param max_rpm: The maximum RPM value.
    """
    # Draw the gauge background
    gauge_surface = pygame.Surface((2 * radius, 2 * radius), pygame.SRCALPHA)
    pygame.draw.circle(gauge_surface, (50, 50, 50), (radius, radius), radius, 0)
    pygame.draw.circle(gauge_surface, (0, 0, 0), (radius, radius), radius - 2, 0)
    screen.blit(gauge_surface, (center_x - radius, center_y - radius))
    
    # Draw the gauge border
    pygame.draw.circle(screen, (255, 255, 255), (center_x, center_y), radius, 2)

    # Draw the redline area
    redline_start_rpm = max_rpm * 0.85  # Redline starts at 85% of max RPM
    redline_start_angle = math.radians(180 - (redline_start_rpm / max_rpm * 180))
    redline_end_angle = math.radians(180)

    pygame.draw.arc(screen, (255, 0, 0), (center_x - radius, center_y - radius, 2 * radius, 2 * radius),
                    redline_start_angle, redline_end_angle, 8)

    # Draw the gauge ticks and labels
    font = pygame.freetype.SysFont('Arial', 18)
    for i in range(0, 361, 30):
        angle = math.radians(i)
        x = center_x + int((radius - 10) * math.cos(angle))
        y = center_y - int((radius - 10) * math.sin(angle))
        tick_length = 10 if i % 60 == 0 else 5
        pygame.draw.line(screen, (255, 255, 255), (x, y), 
                         (x - tick_length * math.cos(angle), y + tick_length * math.sin(angle)), 2)
        
        # Label RPM ticks
        if i % 60 == 0:  # Label every 60 degrees
            label_rpm = int(max_rpm * (i / 360))
            label_text = f"{label_rpm}"
            text_surface, _ = font.render(label_text, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(x, y - 25))
            screen.blit(text_surface, text_rect)

    # Draw the needle with a modern design
    needle_angle = math.radians(180 - (rpm / max_rpm * 180))
    needle_x = center_x + int((radius - 20) * math.cos(needle_angle))
    needle_y = center_y - int((radius - 20) * math.sin(needle_angle))
    pygame.draw.line(screen, (255, 0, 0), (center_x, center_y), (needle_x, needle_y), 4)
    
    # Draw the RPM text in the center
    font = pygame.freetype.SysFont('Arial', 24, bold=True)
    rpm_text, _ = font.render(f"{int(rpm)} RPM", (255, 255, 255))
    text_rect = rpm_text.get_rect(center=(center_x, center_y + radius // 2 - 10))
    screen.blit(rpm_text, text_rect)

def main():
    pygame.init()
    pygame.freetype.init()  # Initialize the freetype module for better font rendering
    
    # Constants
    SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    
    # Create screen
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Engine Simulation")

    # Create engine and gearbox instances
    # engine = Engine("2.0L SkyActiv-G", "Mazda", None, 4, 1998, 83.5, 91.2, 13.0, 6000, 155, 114, 200, 85, "Direct", 4000, 6000)
    engine = Engine("M15A-FXE", "Toyota", "3 Cylinder Engine", 3, 1490, 80.5, 97.6, 14.0, 5500, 91, 67, 120, 91, "EFI", 4800, 5500) # Toyota Yaris
    # gearbox = Gearbox(gear_ratios=[3.454, 2.043, 1.308, 1, 0.759, 0.634], tire_size="195/50R16", final_drive_ratio=3.636)  # Example ratios and tire circumference
    gearbox = Gearbox(gear_ratios=[3.545, 1.913, 1.310, 1.027, 0.850], final_drive_ratio=4.294, tire_size="195/55R16")
    
    clock = pygame.time.Clock()
    
    slider_x, slider_y = 50, 500
    slider_width, slider_height = 300, 20
    slider_value = 0.0

    gauge_x, gauge_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
    gauge_radius = 150

    engine.calculate_increase_rate(gearbox.get_current_ratio())

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                if slider_y <= mouse_y <= slider_y + slider_height and slider_x <= mouse_x <= slider_x + slider_width:
                    slider_value = (mouse_x - slider_x) / slider_width
                    slider_value = min(max(slider_value, 0.0), 1.0)  # Clamp between 0.0 and 1.0
                    engine.throttle = slider_value
            elif event.type == pygame.MOUSEMOTION and event.buttons[0] == 1:
                mouse_x, mouse_y = event.pos
                if slider_y <= mouse_y <= slider_y + slider_height and slider_x <= mouse_x <= slider_x + slider_width:
                    slider_value = (mouse_x - slider_x) / slider_width
                    slider_value = min(max(slider_value, 0.0), 1.0)  # Clamp between 0.0 and 1.0
                    engine.throttle = slider_value
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    gearbox.shift_up()
                    engine.calculate_increase_rate(gearbox.get_current_ratio())
                elif event.key == pygame.K_DOWN:
                    gearbox.shift_down()
                    engine.calculate_increase_rate(gearbox.get_current_ratio())

        engine.update_rpm()

        # Update the gearbox speed
        speed_kph = gearbox.get_speed(engine.current_rpm)

        # Clear screen
        screen.fill(WHITE)

        # Draw slider
        draw_slider(screen, slider_x, slider_y, slider_width, slider_height, slider_value)

        # Draw RPM gauge
        draw_rpm_gauge(screen, gauge_x, gauge_y, gauge_radius, engine.current_rpm, engine.max_rpm)

        # Render engine data
        font = pygame.freetype.SysFont('Arial', 24)
        hp_text, _ = font.render(f"HP: {engine.current_hp:.2f}", BLACK)
        torque_text, _ = font.render(f"Torque: {engine.current_torque_nm:.2f} Nm", BLACK)
        speed_text, _ = font.render(f"Speed: {speed_kph:.2f} km/h", BLACK)
        gear_text, _ = font.render(f"Gear: {gearbox.current_gear}", BLACK)
        throttle_text, _ = font.render(f"Throttle: {engine.throttle}", BLACK)
        
        screen.blit(hp_text, (50, 100))
        screen.blit(torque_text, (50, 150))
        screen.blit(speed_text, (50, 200))
        screen.blit(gear_text, (50, 250))
        screen.blit(throttle_text, (50, 300))

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
