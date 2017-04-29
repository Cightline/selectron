// This #include statement was automatically added by the Particle IDE.
#include <AssetTracker.h>



//YOU SHOULD BE ABLE TO TEST IT NOW AGAINST THE WALL OR SOMETHING

//TODO 
// LOW BATTERY SLEEP (DONT NEED, USING DEEP CYCLE)
// ACELLEROMETER SETUP
// WEB HOOKS FOR CALLING HOME ON ALERT
// FIX GPS
// WILL PROBABLY HAVE TO ADJUST SENSITIVITY 
// CREATE DISCONNECTED/DEAD SENSOR CHECK, OTHERWISE IT WILL LOOP FOREVER
// INCLUDE LOW BATTERY SLEEP MODE
// BEAM BROKEN PRERSISTENCE AND ACKNOWLEDGEMENT


FuelGauge fuel;

AssetTracker t = AssetTracker();

int led1        = D0; 
int led2        = D7;
int sonar_pin   = D3;
int sonar_value = 0;


int8_t array_size       = 9;
uint16_t range_value[]  = {0,0,0,0,0,0,0,0,0};
int calibrated_distance = -1;
bool calibrated         = false;
bool beam_broken        = false;

//not calibrated, etc..
String errors[] = {"",""};


int remote_command(String command);

//ERRORS
// I could make an array for this, but I'm lazy
bool calibrated_error = false;


void setup() 
{
    // SO I CAN TEST, REMOVE LATER
    //Cellular.off();
    
    t.begin();
    t.gpsOn();
    
    Serial.begin(9600);
    
    Serial.println("trying to connect");
    
    
    // REMOTE STUFF
    Particle.function("c", remote_command);
    
    Serial.println("connected");
    
    pinMode(led1,      OUTPUT);
    pinMode(led2,      OUTPUT);
    pinMode(sonar_pin, INPUT);

}

void isort(uint16_t *a, int8_t n)
{
  for (int i = 1; i < n; ++i)  {
    uint16_t j = a[i];
    int k;
    for (k = i - 1; (k >= 0) && (j < a[k]); k--) {
      a[k + 1] = a[k];
    }
    a[k + 1] = j;
  }
}


uint16_t mode(uint16_t *x,int n)
{
  int i = 0;
  int count = 0;
  int maxCount = 0;
  uint16_t mode = 0;
  int bimodal;
  int prevCount = 0;
  while(i<(n-1)){
    prevCount=count;
    count=0;
    while( x[i]==x[i+1] ) {
      count++;
      i++;
    }
    if( count > prevCount & count > maxCount) {
      mode=x[i];
      maxCount=count;
      bimodal=0;
    }
    if( count == 0 ) {
      i++;
    }
    if( count == maxCount ) {      //If the dataset has 2 or more modes.
      bimodal=1;
    }
    if( mode==0 || bimodal==1 ) {  // Return the median if there is no mode.
      mode=x[(n/2)];
    }
    return mode;
  }
}


uint16_t read_distance()
{
    // RETURNS THE "MODE" FOR THE ULTRASONIC SENSOR
    int16_t pulse;
    
    int i = 0;
    
    while(i < array_size)
    {
        pulse = pulseIn(sonar_pin, HIGH);
        range_value[i]=pulse/147;
        if( range_value[i] < 253.9 && range_value[i] >= 5.9 ) i++;  // ensure no values out of range
    }
    
    isort(range_value, array_size);
    
    return mode(range_value, array_size);
}




int calibrate_distance()
{
    uint16_t c_array[]  = {0,0,0};
    calibrated_distance = -1;
    calibrated          = false;


    //collect 3 values from the sensor
    //compare the values to see if they are all the same
    
    
    Serial.println("calibrating");
    for (int b = 0; b <= 50; b++)
    {
        // this is switched to false if the array values don't match
        bool check = true;
        
        //fill the array
        for (int i = 0; i <= 2; i++)
        {
            c_array[i] = read_distance();
        }
        
        // make sure all values are the same
        for (int i = 0; i <= 2; i++)
        {
            if (c_array[i] != c_array[0])
            {
                check = false;
            }
        }
        
        // if check still equals true
        if (check == true)
        {
            calibrated = true;
            calibrated_distance = c_array[0];
            
            Serial.print("calibrated to ");
            Serial.println(calibrated_distance);
        
            Particle.publish("S", "calibrated", PRIVATE);
            return calibrated_distance;
        }
        
        // if we can't calibrate
        
        Serial.println("unable to calibrate distance");
        
        //publish this event
        
        if (calibrated_error == false)
        {
            calibrated_error = true;
            Particle.publish("E", "not_calibrated", PRIVATE);
            return -1;
        }
    }
    
    return -1;
}


bool check_for_movement()
{
    uint16_t current_distance = read_distance();
    
    if (current_distance != calibrated_distance)
    {
        return true;
    }
    
    return false;
}


void loop() 
{
    digitalWrite(led1, LOW);
    digitalWrite(led2, LOW);
 
    
    t.updateGPS();
    
    
    Serial.println("testing");
    
    if (calibrated == false)
    {
        calibrate_distance();
    }
    
    
    // Check for movment. If movment is detected, publish it and mark beam_broken as true. This stops it from sending 
    // the same message over and over. 
    
    if (check_for_movement() == true)
    {
        if (beam_broken == false)
        {
            beam_broken = true;
            // M for movement, t for true. 
            Particle.publish("S", "detected_movement", PRIVATE);
        }
    }
    
    if (beam_broken == true)
    {
        Serial.println("BEAM BROKEN");
    }
    
    Serial.println("current distance: " + read_distance());
    Serial.println("battery soc: " + String::format("%.2f", fuel.getSoC()));
    Serial.println(t.preNMEA());
    
    
    
    
    
    if (t.gpsFix())
    {
        Serial.println("gps fix: yes");
    }
    
    else
    {
        Serial.println("gps fix: no");
    }
    
    digitalWrite(led1, HIGH);
    digitalWrite(led2, HIGH);

}

// REMOTE FUNCTIONS

int remote_command(String command)
{
    if (command == "state")
    {
        return (int) fuel.getSoC();
    }
    
    else if (command == "recalibrate")
    {
        calibrate_distance();
        beam_broken = false;
        return calibrated_distance;
    }
    
    else if (command == "location")
    {
        if (t.gpsFix())
        {
            Particle.publish("GPS", t.readLatLon(), PRIVATE);
            return 0;
        }
        
        else
        {
            return -1;
        }
    }
    
    
    return -2;
}
