#include <Arduino_BMI270_BMM150.h>
#include <MadgwickAHRS.h>

Madgwick filter;
unsigned long microsPerReading, microsPrevious;

// Calibration parameters for magnetometer
float magOffsetX, magOffsetY, magOffsetZ;
float magScaleX = 1.0, magScaleY = 1.0, magScaleZ = 1.0;
// Calibration parameters for gyroscope
float gyroOffsetX = 0, gyroOffsetY = 0, gyroOffsetZ = 0;
// Calibration parameters for accelerometer
float accelOffsetX = 0, accelOffsetY = 0, accelOffsetZ = 0;
float accelScaleX = 1.0, accelScaleY = 1.0, accelScaleZ = 1.0;

void setup() {
  Serial.begin(115200); // Increase baud rate to handle higher frequency data output
  while (!Serial);

  // Try to initialize IMU
  if (!IMU.begin()) {
    Serial.println("Failed to initialize IMU!");
    while (1);
  }

  Serial.println("IMU initialized successfully!");

  // Calibrate sensors
  calibrateGyroscope();
  calibrateAccelerometer();
  calibrateMagnetometer();

  // Set sampling rate (e.g., 100 Hz) and beta parameter
  filter.begin(100);
  // filter.setBeta(0.8); // Adjust beta parameter to improve stability
  microsPerReading = 1000000 / 100;
  microsPrevious = micros();
}

void loop() {
  float ax, ay, az;
  float gx, gy, gz;
  float mx, my, mz;

  // Check if it's time for the next sample
  if (micros() - microsPrevious >= microsPerReading) {
    microsPrevious += microsPerReading;

    // Read accelerometer data
    if (IMU.readAcceleration(ax, ay, az)) {
      // Apply accelerometer calibration
      ax = (ax - accelOffsetX) / accelScaleX;
      ay = (ay - accelOffsetY) / accelScaleY;
      az = (az - accelOffsetZ) / accelScaleZ;
    }

    // Read gyroscope data
    if (IMU.readGyroscope(gx, gy, gz)) {
      // Apply gyroscope calibration
      gx -= gyroOffsetX;
      gy -= gyroOffsetY;
      gz -= gyroOffsetZ;
    }

    // Read magnetometer data
    if (IMU.readMagneticField(mx, my, mz)) {
      // Calibrate magnetometer data
      mx = (mx - magOffsetX) / magScaleX;
      my = (my - magOffsetY) / magScaleY;
      mz = (mz - magOffsetZ) / magScaleZ;
    }

    // Update Madgwick filter
    filter.update(gx, gy, gz, ax, ay, az, mx, my, mz);

    // Get Euler angles
    float roll = filter.getRoll();
    float pitch = filter.getPitch();
    float yaw = filter.getYaw();

    // Output Euler angles
    Serial.print(roll);
    Serial.print('\t');
    Serial.print(pitch);
    Serial.print('\t');
    Serial.println(yaw);
  }
}

void calibrateGyroscope() {
  Serial.println("Starting gyroscope calibration...");
  delay(5000); // Give user 5 seconds to keep the sensor still

  float sumX = 0, sumY = 0, sumZ = 0;
  const int sampleCount = 1000;

  for (int i = 0; i < sampleCount; i++) {
    if (IMU.readGyroscope(gyroOffsetX, gyroOffsetY, gyroOffsetZ)) {
      sumX += gyroOffsetX;
      sumY += gyroOffsetY;
      sumZ += gyroOffsetZ;
      delay(5);
    }
  }

  // Calculate average offset
  gyroOffsetX = sumX / sampleCount;
  gyroOffsetY = sumY / sampleCount;
  gyroOffsetZ = sumZ / sampleCount;

  Serial.println("Gyroscope calibration complete.");
  Serial.print("OffsetX: ");
  Serial.print(gyroOffsetX);
  Serial.print(" OffsetY: ");
  Serial.print(gyroOffsetY);
  Serial.print(" OffsetZ: ");
  Serial.println(gyroOffsetZ);
}

void calibrateAccelerometer() {
  Serial.println("Starting accelerometer calibration...");
  Serial.println("Place the sensor still on a flat surface for 60 seconds.");
  delay(5000); // Give user 5 seconds to keep the sensor still

  float minX = 32767, minY = 32767, minZ = 32767;
  float maxX = -32768, maxY = -32768, maxZ = -32768;

  unsigned long startTime = millis();
  while (millis() - startTime < 60000) {
    float x, y, z;
    if (IMU.readAcceleration(x, y, z)) {
      if (x < minX) minX = x;
      if (y < minY) minY = y;
      if (z < minZ) minZ = z;
      if (x > maxX) maxX = x;
      if (y > maxY) maxY = y;
      if (z > maxZ) maxZ = z;
    }
  }

  // Calculate calibration offset and scale
  accelOffsetX = (maxX + minX) / 2.0;
  accelOffsetY = (maxY + minY) / 2.0;
  accelOffsetZ = (maxZ + minZ) / 2.0;

  accelScaleX = (maxX - minX) / 2.0;
  accelScaleY = (maxY - minY) / 2.0;
  accelScaleZ = (maxZ - minZ) / 2.0;

  Serial.println("Accelerometer calibration complete.");
  Serial.print("OffsetX: ");
  Serial.print(accelOffsetX);
  Serial.print(" OffsetY: ");
  Serial.print(accelOffsetY);
  Serial.print(" OffsetZ: ");
  Serial.println(accelOffsetZ);

  Serial.print("ScaleX: ");
  Serial.print(accelScaleX);
  Serial.print(" ScaleY: ");
  Serial.print(accelScaleY);
  Serial.print(" ScaleZ: ");
  Serial.println(accelScaleZ);
}

void calibrateMagnetometer() {
  Serial.println("Starting magnetometer calibration...");
  Serial.println("Move the sensor in a figure 8 pattern until calibration is complete.");
  delay(5000); // Give user 5 seconds to start moving the sensor

  float minX = 32767, minY = 32767, minZ = 32767;
  float maxX = -32768, maxY = -32768, maxZ = -32768;

  unsigned long startTime = millis();
  while (millis() - startTime < 5000) { // Decreased calibration time to 5 seconds
    float x, y, z;
    if (IMU.magneticFieldAvailable()) {
      IMU.readMagneticField(x, y, z);
      if (x < minX) minX = x;
      if (y < minY) minY = y;
      if (z < minZ) minZ = z;
      if (x > maxX) maxX = x;
      if (y > maxY) maxY = y;
      if (z > maxZ) maxZ = z;
    }
  }

  // Calculate calibration offset and scale
  magOffsetX = (maxX + minX) / 2.0;
  magOffsetY = (maxY + minY) / 2.0;
  magOffsetZ = (maxZ + minZ) / 2.0;

  magScaleX = (maxX - minX) / 2.0;
  magScaleY = (maxY - minY) / 2.0;
  magScaleZ = (maxZ - minZ) / 2.0;

  Serial.println("Magnetometer calibration complete.");
  Serial.print("OffsetX: ");
  Serial.print(magOffsetX);
  Serial.print(" OffsetY: ");
  Serial.print(magOffsetY);
  Serial.print(" OffsetZ: ");
  Serial.println(magOffsetZ);

  Serial.print("ScaleX: ");
  Serial.print(magScaleX);
  Serial.print(" ScaleY: ");
  Serial.print(magScaleY);
  Serial.print(" ScaleZ: ");
  Serial.println(magScaleZ);
  delay(5000);
}
