from phoenix6 import controls, configs, hardware, signals, unmanaged

talonfx = hardware.TalonFX(0)

# Get the position signal
position_signal = talonfx.get_position()
encoder_value = position_signal.value
print(f"Current encoder value: {encoder_value}")
