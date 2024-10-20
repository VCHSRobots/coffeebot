#include <Arduino_BMI270_BMM150.h> // IMU library for accelerometer, gyroscope, and magnetometer
#include <MadgwickAHRS.h>           // Madgwick sensor fusion algorithm

Madgwick filter;
float gx, gy, gz;   // Gyroscope values
float ax, ay, az;   // Accelerometer values
float mx, my, mz;   // Magnetometer values
float gx_min = 0, gy_min = 0, gz_min = 0; // Gyroscope min values
float gx_max = 0, gy_max = 0, gz_max = 0; // Gyroscope max values
float gx_threshold = 0, gy_threshold = 0, gz_threshold = 0;

void setup() {
  Serial.begin(9600);
  while (!Serial);

  // Initialize IMU (BMI270 and BMM150)
  if (!IMU.begin()) {
    Serial.println("Failed to initialize IMU!");
    while (1);
  }

  // Calibrate gyroscope (determine min/max thresholds)
  calibrateGyroscope();

  // Set up Madgwick filter with a sample frequency (in Hz)
  filter.begin(100);

  Serial.println("IMU initialized successfully");
}

void loop() {
  // Read IMU (accelerometer, gyroscope, and magnetometer) data
  if (IMU.accelerationAvailable() && IMU.gyroscopeAvailable() && IMU.magneticFieldAvailable()) {
    IMU.readAcceleration(ax, ay, az);
    IMU.readGyroscope(gx, gy, gz);
    IMU.readMagneticField(mx, my, mz);

    // Apply gyroscope thresholding and bias correction
    gx = applyGyroCorrection(gx, gx_min, gx_max, gx_threshold);
    gy = applyGyroCorrection(gy, gy_min, gy_max, gy_threshold);
    gz = applyGyroCorrection(gz, gz_min, gz_max, gz_threshold);
  }

  // Update Madgwick filter with sensor data
  filter.update(gx, gy, gz, ax, ay, az, mx, my, mz);

  // Get the estimated orientation as Euler angles
  float roll = filter.getRoll();
  float pitch = filter.getPitch();
  float yaw = filter.getYaw();

  // Print the orientation in Roll, Pitch, Yaw format
  Serial.print("Roll: ");
  Serial.print(roll);
  Serial.print("\tPitch: ");
  Serial.print(pitch);
  Serial.print("\tYaw: ");
  Serial.println(yaw);

  delay(10); // Delay to limit data rate (adjust as needed)
}

void calibrateGyroscope() {
  const int num_samples = 100;
  gx_min = gy_min = gz_min = 1000;
  gx_max = gy_max = gz_max = -1000;

  Serial.println("Calibrating gyroscope, please keep the board still...");

  for (int i = 0; i < num_samples; i++) {
    while (!IMU.gyroscopeAvailable());
    IMU.readGyroscope(gx, gy, gz);

    if (gx < gx_min) gx_min = gx;
    if (gy < gy_min) gy_min = gy;
    if (gz < gz_min) gz_min = gz;

    if (gx > gx_max) gx_max = gx;
    if (gy > gy_max) gy_max = gy;
    if (gz > gz_max) gz_max = gz;

    delay(10);
  }

  gx_threshold = 2 * (gx_max - gx_min);
  gy_threshold = 2 * (gy_max - gy_min);
  gz_threshold = 2 * (gz_max - gz_min);

  Serial.println("Gyroscope calibration complete");
}

float applyGyroCorrection(float g, float g_min, float g_max, float g_threshold) {
  float g_offset = (g_max + g_min) / 2;
  if (g > -g_threshold && g < g_threshold) {
    return 0;
  } else {
    return g - g_offset;
  }
}
