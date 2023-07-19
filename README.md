# ID Card Detector

ID Card Detector is a web application that allows users to capture images of their ID cards using their device's camera. The application then processes the images to extract relevant information and verify the identity of the user.

## Features

- Live capture of ID card images using the device's camera
- Extraction of relevant information from the ID card
- Verification of the user's identity based on the extracted information
- User-friendly interface for capturing and viewing ID card images

## Getting Started

These instructions will help you set up the project on your local machine for development and testing purposes.

### Prerequisites

- Python 3.8 or higher
- Django 3.2 or higher
- A webcam or camera-enabled device for capturing images

### Installation

1. Clone the repository to your local machine:

2. Change to the project directory:

3. Create a virtual environment and activate it:

4. Install the required dependencies:

5. Install important module
#### Ubuntu: 

```sh

sudo apt-get update
sudo apt-get install build-essential cmake
sudo apt-get install libopenblas-dev liblapack-dev 
sudo apt-get install libx11-dev libgtk-3-dev
sudo apt-get install python3 python3-dev python3-pip
```
### Mac:
```sh

brew install cmake pkg-config
brew install jpeg libpng libtiff openexr
brew install eigen tbb
```
#### Other Requirements
```shell
pip3 install dlib
pip install opencv-python
pip install mtcnn
pip install -r requirements.txt
```


6. Apply database migrations
   1. ```python manage.py makmigrations```
   2. ```python manage.py migrate```
7. Create Super User:
   1. ```python manage.py createsuperuser```


8. Open your web browser and navigate to `http://127.0.0.1:8000/` to access the application.

## Usage

1. On the home page, Enter Name and start then click the "Capture ID Card" button to access the camera interface.
2. Position your ID card within the camera's view and click the "Capture" button to take a photo.
3. The application will process the image and display the extracted information and verification status.
4. Then the application will take Your live video and recognise you are the same person as ID card.
5. You can view a list of previously captured ID cards and their details on the "Recognition List" page.
6. You can view Each Recognized Card Detail.

