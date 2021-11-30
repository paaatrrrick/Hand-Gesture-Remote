# Hand-Gesture-Remote
![remoteControl](https://user-images.githubusercontent.com/88113528/143988010-a5603977-9287-4b9d-b148-721e32828718.gif =250x250)
## Quick Use
Download, replace ROKU_API_KEY with you tv's address, install Mediapipe, and OpenCv

## Explanation
Using only a generic webcam, recorded hand gestures acted as a remote control for this Roku T.V. Gesutres including all directional motions, go back, power on, and select (still being worked on). OpenCv paired with Mediapipe gives 21 hand landmarks for x,y,z coordinates. Algorithms then recognize gestures out of these landmarks which is then sent to the Roku API.
