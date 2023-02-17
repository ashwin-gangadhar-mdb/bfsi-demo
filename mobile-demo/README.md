#  BFSI Fraudlent Transaction Mobile App
This is a React Native app that runs on both iOS and Android which demonstrates the usecase of BFSI Fraudlent Transaction.

## Prerequisites
Before running the app, you'll need to have the following installed on your system:
- Python 3
- pip3
- Node.js
- npm or Yarn
- React Native CLI
- Xcode (for iOS)
- Android Studio (for Android)

## Deploy the Backend Service
- Clone this repository to your local machine.
    ```bash
    git clone https://github.com/ashwin-gangadhar-mdb/bfsi-demo.git
    cd mobile-demo/backend-service
    ```

- Update the MongoDB Connection String in the following file.
    - `mobile-demo/backend-service/serve.py`

- Install the project dependencies using pip
    ```
    pip3 install -r req.txt
    ```
- Run the Python code.
    ```
    python3 serve.py
    ```

## Running the App
- Clone this repository to your local machine.
    ```bash
    git clone https://github.com/ashwin-gangadhar-mdb/bfsi-demo.git
    ```
- Install the dependencies using npm or Yarn.
    ```bash
    cd mobile-demo
    npm install
    ```
    OR
    ```bash
    cd mobile-demo
    yarn install
    ```

- Update the API credentials and Endpoints in the following location
    - `mobile-demo/react-native-app/src/screens/LoginScreen.js`
    - `mobile-demo/react-native-app/src/screens/TransactionScreen.js`

- Start the React Native Metro Bundler in a separate terminal window.
```bash
npm start
```
OR
```bash
yarn start
```

- For iOS, run the following command in the project root directory to install the iOS dependencies:
    ```bash
    cd ios && pod install && cd ..
    ```

- For iOS, open the Xcode project file in the ios directory and build the app using the Xcode IDE.

- For Android, open Android Studio and import the project directory. Then build and run the app using the Android Studio IDE.

- If everything is set up correctly, the app should now be running on your iOS or Android device.