import React, { useEffect, useState } from "react";
import {
  View,
  Text,
  TouchableOpacity,
  TextInput,
  StyleSheet,
  Alert
} from "react-native";

import { useTheme } from "react-native-paper";
import Icon from "react-native-vector-icons/MaterialCommunityIcons";
import FontAwesome from "react-native-vector-icons/FontAwesome5";
import Feather from "react-native-vector-icons/Feather";
import Animated from "react-native-reanimated";
import Button from '../components/Button'
import BusyIndicator from "../components/BusyIndicator";
import axios from "axios";
import { Picker } from "@react-native-picker/picker";

const TransactionScreen = ({ route, navigation }) => {
  const { data } = route.params;
  const { colors } = useTheme();
  const [isLoading, setIsLoading] = useState(false);
  const [indicatorMessage, setIndicatorMessage] = useState("Fetching merchants..");
  const [merchantsInfo, setMerchantsInfo] = useState(false);
  const [selectedMerchant, setSelectedMerchant] = useState(null);
  const [selectedStreet, setSelectedStreet] = useState(null);
  const [amount, setAmount] = useState('');
  const amountInput = React.createRef();
  const showAlert = (title, message) => {
    Alert.alert(
      title,
      message,
      [{ text: "OK", onPress: () => {} }],
      { cancelable: false }
    );
  };

  const loadMerchants = async () => {
    setIsLoading(true);
    try {
      const response = await axios({
        method: "post",
        url: "https://data.mongodb-api.com/app/data-xfgbp/endpoint/data/v1/action/find",
        headers: {
          "Content-Type": "application/json",
          "Access-Control-Request-Headers": "*",
          "api-key":
            "xxxx",
        },
        data: JSON.stringify({
          collection: "merchants",
          database: "fraud-detection",
          dataSource: "BFSI-demo",
          limit: 100,
        }),
      });
      console.log(response.data);
      setMerchantsInfo(response.data.documents);
      setIsLoading(false);
    } catch (error) {
      setIsLoading(false);
      console.error(error);
      showAlert(
        "Error",
        "Failed to load merchants Info. An error has occurred, Reason: " +
          JSON.stringify(error)
      );
    }
  };

  const makeID = (length) => {
    let result = '';
    const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    const charactersLength = characters.length;
    let counter = 0;
    while (counter < length) {
      result += characters.charAt(Math.floor(Math.random() * charactersLength));
      counter += 1;
    }
    return result;
}

  const onStartTransactionPressed = async () => {
    setIndicatorMessage("Transaction in progress...")
    setIsLoading(true);
    console.log("vi" + selectedMerchant )
    console.log("safds" + selectedStreet)
    var payload = merchantsInfo.find((merchant) => merchant.merchant == selectedMerchant && merchant.street == selectedStreet);

    const date = new Date();
    const year = date.getFullYear();
    const month = ('0' + (date.getMonth() + 1)).slice(-2);
    const day = ('0' + date.getDate()).slice(-2);
    const hour = ('0' + date.getHours()).slice(-2);
    const minute = ('0' + date.getMinutes()).slice(-2);
    const second = ('0' + date.getSeconds()).slice(-2);
    const formattedDate = `${year}-${month}-${day} ${hour}:${minute}:${second}`;

    var payload_data = JSON.stringify({
      trans_date_trans_time: formattedDate,
      cc_num: data.cc_num.toString(),
      merchant: payload.merchant,
      category: payload.category,
      amt: amount,
      first: data.first,
      last: data.last,
      gender: data.gender,
      street: payload.street,
      city: "Elizabeth",
      state: payload.state,
      zip: payload.zip.toString(),
      job: "Operational researcher",
      lat: (payload.merch_lat+ 1).toString(),
      long: payload.merch_long.toString(),
      city_pop: payload.city_pop.toString(),
      dob: data.dob,
      trans_num: makeID(20),
      unix_time: Math.round((new Date()).getTime() / 1000).toString(),
      merch_lat: payload.merch_lat.toString(),
      merch_long: payload.merch_long.toString(),
      is_fraud: '0'
    })
    console.log(payload_data)
    try {
      const response = await axios({
        method: 'post',
        url: 'http://52.30.16.82:8889/initiate/txn',
        headers: {
          'Content-Type': 'application/json'
        },
        data: payload_data
      });
      console.log(response);
      this.amountInput.clear();
      setSelectedMerchant(null)
      setSelectedStreet(null)
      setIsLoading(false)
      if(response.data.txn_status == "REJECTED") {
        showAlert('REJECTED', 'Your transaction was unsuccessful. Please get in touch with customer support for further details!');
      } else {
        showAlert('AUTHORIZED', '$' + amount + ' is successfully credited to ' + selectedMerchant.replace("fraud_", "")+ '!');
      }
     
    } catch (error) {
      setIsLoading(false)
      console.error(error);
      showAlert('Error', 'Failed to initiate a transaction, Reason: '+ JSON.stringify(error));
    }
  }


  renderHeader = () => (
    <View style={styles.header}>
      <View style={styles.panelHeader}>
        <View style={styles.panelHandle} />
      </View>
    </View>
  );

  bs = React.createRef();
  fall = new Animated.Value(1);

  useEffect(() => {
    loadMerchants();
  }, []);

  return (
    <View style={styles.container}>
      <Animated.View
        style={{
          margin: 20,
          opacity: Animated.add(0.1, Animated.multiply(this.fall, 1.0)),
        }}
      >
        {isLoading && (
          <BusyIndicator visible={isLoading} message={indicatorMessage} />
        )}
        <View style={styles.action}>
          <FontAwesome name="store" color={colors.text} size={20} />
          <Text style={[ styles.textInput, { color: colors.text } ]}>
            Merchant
          </Text>
        </View>
        <View style={styles.dropdown}>
          <Picker
            mode="dropdown"
            selectedValue={selectedMerchant}
            style={styles.picker}
            onValueChange={(merchant) => setSelectedMerchant(merchant)}
          >
            <Picker.Item label="Select a Merchant" value={null} />
            {merchantsInfo && merchantsInfo.map((data) => (
              <Picker.Item
                key={data.merchant}
                label={data.merchant.replace("fraud_", "")}
                value={data.merchant}
              />
            ))}
          </Picker>
        </View>
        <View style={styles.action}>
        <FontAwesome name="location-arrow" color={colors.text} size={20} />
          <Text style={[ styles.textInput, { color: colors.text } ]}>
            Street Name
          </Text>
        </View>
        <View style={styles.dropdown}>
          <Picker
            mode="dropdown"
            selectedValue={selectedStreet}
            style={styles.picker}
            onValueChange={(street) => setSelectedStreet(street)} >
            <Picker.Item label="Select a street" value={null} itemStyle={styles.textInput}/>
            {selectedMerchant && merchantsInfo.filter((merchant) => merchant.merchant == selectedMerchant).map((item) => (
              <Picker.Item
                key={item.street}
                label={item.street}
                value={item.street}
              />
            ))}
          </Picker>
        </View>
        <View style={styles.action}>
          <FontAwesome name="dollar-sign" color={colors.text} size={20} />
          <Text style={[ styles.textInput, { color: colors.text } ]}>
            Amount
          </Text>
        </View>
        <View style={styles.action}>
        <TextInput
            placeholder="Enter the Amount"
            placeholderTextColor="#666666"
            keyboardType="numeric"
            autoCorrect={false}
            ref={input => { this.amountInput = input }}
            onChangeText={(value) => setAmount(value)}
            style={[ styles.textBar,{ color: colors.text,} ]} />
        </View>
        {/* <TouchableOpacity style={styles.commandButton} onPress={() => {onStartTransactionPressed}}>
          <Text style={styles.panelButtonTitle} onPress={() => {onStartTransactionPressed}} >Initiate Transaction</Text>
        </TouchableOpacity> */}
        <Button style={styles.commandButton}  mode="contained" onPress={onStartTransactionPressed}>
        Pay
      </Button>
      </Animated.View>
    </View>
  );
};

export default TransactionScreen;

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  picker: {
    flex: 1,
    paddingLeft: 10,
    height: 200
  },
  commandButton: {
    padding: 15,
    borderRadius: 10,
    backgroundColor: "#00684A",
    alignItems: "center",
    marginTop: 20,
  },
  panel: {
    padding: 20,
    backgroundColor: "#FFFFFF",
    paddingTop: 20,
    // borderTopLeftRadius: 20,
    // borderTopRightRadius: 20,
    // shadowColor: '#000000',
    // shadowOffset: {width: 0, height: 0},
    // shadowRadius: 5,
    // shadowOpacity: 0.4,
  },
  header: {
    backgroundColor: "#FFFFFF",
    shadowColor: "#333333",
    shadowOffset: { width: -1, height: -3 },
    shadowRadius: 2,
    shadowOpacity: 0.4,
    // elevation: 5,
    paddingTop: 20,
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
  },
  panelHeader: {
    alignItems: "center",
  },
  panelHandle: {
    width: 40,
    height: 8,
    borderRadius: 4,
    backgroundColor: "#00000040",
    marginBottom: 10,
  },
  panelTitle: {
    fontSize: 27,
    height: 35,
  },
  panelSubtitle: {
    fontSize: 14,
    color: "gray",
    height: 30,
    marginBottom: 10,
  },
  panelButton: {
    padding: 13,
    borderRadius: 10,
    backgroundColor: "#FF6347",
    alignItems: "center",
    marginVertical: 7,
  },
  panelButtonTitle: {
    fontSize: 17,
    fontWeight: "bold",
    color: "white",
  },
  action: {
    flexDirection: "row",
    marginTop: 5,
  },
  dropdown: {
    flexDirection: "row",
    alignItems: 'center'
  },
  actionError: {
    flexDirection: "row",
    marginTop: 10,
    borderBottomWidth: 1,
    borderBottomColor: "#FF0000",
    paddingBottom: 5,
  },
  textInput: {
    flex: 1,
    marginTop: Platform.OS === "ios" ? 0 : -12,
    paddingLeft: 10,
    color: "#05375a",
  },
  textBar: {
    flex: 1,
    marginTop: 20,
    marginBottom: 20,
    fontSize: 20,
    paddingLeft: 10,
    color: "#05375a",
  },
});
