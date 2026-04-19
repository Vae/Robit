#include <AccelStepper.h>

#define STEPPERS 2

#define FULLSTEP 4
#define HALFSTEP 8

//int16_t reportInterval = INT16_MAX;
int16_t reportInterval = 0;
bool reportAtPositionReached = true;
#define SERIALBUFFER_MAX 24

AccelStepper stepper1(FULLSTEP, 4, 6, 7, 5);
AccelStepper stepper2(FULLSTEP, 8, 10, 11, 9);


//Do not set anything below ----------------------------------------------------------------

void(* resetFunc) (void) = 0;

#define STEPPER_ITER_P(method, param) for(int i = 0; i < STEPPERS; i++) { if(motors & 0x01) { stepper[i]->method(param); } motors = motors >> 1; }
#define STEPPER_ITER(method) for(int i = 0; i < STEPPERS; i++) { if(motors & 0x01) { stepper[i]->method(); } motors = motors >> 1; }


AccelStepper *stepper[STEPPERS] = {&stepper1, &stepper2};

int reportIteration = 0;
bool reportAtPositionReached_reported = false;

char serialBuffer[SERIALBUFFER_MAX];
char serialIndex = 0;

void setup() {
  Serial.begin(115200);
  for(int i = 0; i < STEPPERS; i++){
    stepper[i]->setMaxSpeed(500.0);
    stepper[i]->setAcceleration(500.0);
    stepper[i]->disableOutputs();
  }

  Serial.println();
  Serial.println(":start");
  reportMovement();
  reportPosition();
}

void reportMovement(){
  Serial.print("A");
  for(int i = 0; i < STEPPERS; i++){
    Serial.print(stepper[i]->acceleration());
    Serial.print(" ");
  }

  Serial.print("X");
  for(int i = 0; i < STEPPERS; i++){
    Serial.print(stepper[i]->maxSpeed());
    Serial.print(" ");
  }

  Serial.println();
}

void reportPosition(){
  reportIteration = 0;
  
  Serial.print("P");
  for(int i = 0; i < STEPPERS; i++){
    Serial.print(stepper[i]->currentPosition());
    Serial.print(" ");
  }
  
  Serial.print("R");
  for(int i = 0; i < STEPPERS; i++){
    Serial.print(stepper[i]->distanceToGo());
    Serial.print(" ");
  }
  
  Serial.print("T");
  for(int i = 0; i < STEPPERS; i++){
    Serial.print(stepper[i]->targetPosition());
    Serial.print(" ");
  }

  Serial.println();
}

//void motor_set

long command_getLong(){
  //serialBuffer is not null-terminated, make sure it is for atoi
  serialBuffer[serialIndex] = '\0';
  return atol(serialBuffer + 3);
}
long command_getFloat(){
  //serialBuffer is not null-terminated, make sure it is for atoi
  serialBuffer[serialIndex] = '\0';
  return atof(serialBuffer + 3);
}
void command_unknown(char unknownChar){
  Serial.print(":? ");
  Serial.println(unknownChar);
  Serial.println();
}

void command_motors(){
  //sanity check: must have at least 3 bytes in the buffer
  if(serialIndex < 3){
    Serial.println(":? \"incomplete\"");
    return;
  }
  uint8_t motors = serialBuffer[1] & 0x0f;
  switch(serialBuffer[2]){
    case 'A': {
      //for(int i = 0; i < STEPPERS; i++) { if(motors & 0x01) { stepper[i]->stop(); } motors = motors >> 1; }
      long value = command_getLong();
      STEPPER_ITER_P(setAcceleration, value);
      reportMovement();
      } break;
    case 'B': {
      long value = command_getFloat();
      //STEPPER_ITER_P(setAccelerationRoot, value);
      reportMovement();
      } break;
    case 'C': {
      long value = command_getLong();
      STEPPER_ITER_P(setCurrentPosition, value);
      } break;
    case 'D': STEPPER_ITER(disableOutputs); break;
    case 'E': STEPPER_ITER(enableOutputs); break;
    case 'M': {
      long value = command_getLong();
      reportAtPositionReached_reported = false;
      STEPPER_ITER_P(move, value);
      } break;
    case 'P': {
      long value = command_getLong();
      reportAtPositionReached_reported = false;
      STEPPER_ITER_P(moveTo, value);
      } break;
    case 'S': {
      long value = command_getLong();
        switch(value){
          case 'B':
            STEPPER_ITER_P(moveTo, stepper[i]->currentPosition());
            //for(int i = 0; i < STEPPERS; i++) { if(motors & 0x01) {
            //      stepper[i]->currentPosition();
            //} motors = motors >> 1; }
            break;
          case 'R':
            STEPPER_ITER_P(setCurrentPosition, 0);
            STEPPER_ITER_P(moveTo, 0);
            break;
          default:
          STEPPER_ITER(stop);
        }
      } break;
    case 's': STEPPER_ITER(stop); break;
    case 'X': {
      long value = command_getLong();
      STEPPER_ITER_P(setMaxSpeed, value);
      reportMovement();
      } break;
    case 'Y': {
      long value = command_getLong();
      STEPPER_ITER_P(setPinsInverted, value);
      } break;
    default:
      command_unknown(serialBuffer[2]);
  }
}

void command_reports(){
  switch(serialBuffer[1]){
    case 'A': {
      long value = command_getLong();
      reportAtPositionReached = true;
      reportAtPositionReached_reported = false;
      } break;
    case 'H':
      Serial.print(":ms ");
      Serial.println(millis());
      break;
    case 'I': {
      long value = command_getLong();
      reportInterval = value;
      reportIteration = 0;
      } break;
    case 'M': reportMovement(); break;
    case 'P': reportPosition(); break;
    default: command_unknown(serialBuffer[1]);
  }
}

void command_systems(){
  switch(serialBuffer[1]){
    case 'R': resetFunc(); break;
    default: command_unknown(serialBuffer[1]);
  }
}

void completeSerialCommand(){
  switch(serialBuffer[0]){
    case 'M':
      command_motors();
      break;
    case 'R':
      command_reports();
      break;
    case 'S':
      command_systems();
      break;
    case '\r':
    case '\n': break;
    default: command_unknown(serialBuffer[0]);
  }
  for(int i = 0; i < SERIALBUFFER_MAX; i++){ serialBuffer[i] = '\0'; }
  serialIndex = 0;
}

void loop() {
  reportIteration++;
  
  if(
      //Is report interval set to auto report and has that interval been reached?
      (reportInterval > 0 and reportIteration == reportInterval) or 
      //or, is reporting when target position reached enabled and have any of the motors reached a position?
      (reportAtPositionReached and reportAtPositionReached_reported == false and stepper1.distanceToGo() == 0 and stepper2.distanceToGo() == 0)){
    reportPosition();
    if(reportAtPositionReached)
      reportAtPositionReached_reported = true;
  }
  if(reportAtPositionReached and reportAtPositionReached_reported and (stepper1.distanceToGo() != 0 or stepper2.distanceToGo() != 0))
    reportAtPositionReached_reported = false;
    
  if(Serial.available() > 0){
    char r = Serial.read();
    if(r == '\n' or r == '\r')
      completeSerialCommand();
    else{
      serialBuffer[serialIndex] = r;
      serialIndex++;
    }
  }
  //if(stepper2.distanceToGo() == 0)
  //  stepper2.moveTo(-stepper2.currentPosition());
  stepper1.run();
  stepper2.run();
}
