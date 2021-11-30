# Hand-Gesture-Remote
![ezgif com-gif-maker (2)](https://user-images.githubusercontent.com/88113528/144082187-69e47560-1740-4171-89ce-fe80c4df0b11.gif)

## Quick Use
Download, replace ROKU_API_KEY with you tv's address, install Mediapipe, and OpenCv.

## Explanation
Using only a generic webcam, recorded hand gestures acted as a remote control for this Roku T.V. Gesutres including all directional motions, power on, and select (still being improved). OpenCv paired with Mediapipe gives 21 hand landmarks for x,y,z coordinates. Algorithms then recognize gestures out of these landmarks which is then sent to the Roku API.
