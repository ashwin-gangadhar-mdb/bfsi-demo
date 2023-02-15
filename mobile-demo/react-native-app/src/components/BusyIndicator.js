import React from 'react';
import { View } from 'react-native';
import Spinner from 'react-native-loading-spinner-overlay';

const BusyIndicator = ({ visible, message }) => {
  return (
    <View style={{flex: 1}}>
      <Spinner
        visible={visible}
        textContent={message}
        textStyle={{color: '#FFF'}}
        overlayColor="rgba(0, 0, 0, 0.5)"
      />
    </View>
  );
};

export default BusyIndicator;