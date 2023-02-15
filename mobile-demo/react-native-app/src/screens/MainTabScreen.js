import React from 'react';

import {createMaterialBottomTabNavigator} from '@react-navigation/material-bottom-tabs';
import {createStackNavigator} from '@react-navigation/stack';

import Icon from 'react-native-vector-icons/Ionicons';
import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';

import HomeScreen from './HomeScreen';
import ProfileScreen from './ProfileScreen';
import TransactionScreen from './TransactionScreen';

import {useTheme, Avatar} from 'react-native-paper';
import {View} from 'react-native-animatable';
import {TouchableOpacity} from 'react-native-gesture-handler';

const HomeStack = createStackNavigator();
const ProfileStack = createStackNavigator();
const TransactionStack = createStackNavigator();

const Tab = createMaterialBottomTabNavigator();

const MainTabScreen = ({ route }) => {
  const { data } = route.params;
  return (
    <Tab.Navigator initialRouteName="Home" activeColor="#00684A">
      <Tab.Screen
        name="HomeScreen"
        component={HomeStackScreen}
        options={{
          tabBarLabel: "Home",
          tabBarColor: "#FF6347",
          tabBarIcon: ({ color }) => (
            <Icon name="ios-home" color={color} size={26} />
          ),
        }}
      />
      <Tab.Screen
        name="Transactions"
        component={TransactionsStackScreen}
        initialParams={{ data: data }}
        options={{
          tabBarLabel: "Transactions",
          tabBarColor: "#d02860",
          tabBarIcon: ({ color }) => (
            <Icon name="cash-outline" color={color} size={26} />
          ),
        }}
      />
      <Tab.Screen
        name="Notifications"
        component={HomeStackScreen}
        options={{
          tabBarLabel: "Updates",
          tabBarColor: "#1f65ff",
          tabBarIcon: ({ color }) => (
            <Icon name="ios-notifications" color={color} size={26} />
          ),
        }}
      />
      <Tab.Screen
        name="ProfileScreen"
        component={ProfileStackScreen}
        initialParams={{ data: data }}
        options={{
          tabBarLabel: "Profile",
          tabBarColor: "#694fad",
          tabBarIcon: ({ color }) => (
            <Icon name="ios-person" color={color} size={26} />
          ),
        }}
      />
    </Tab.Navigator>
  );
};

export default MainTabScreen;

const HomeStackScreen = ({navigation}) => {
  const {colors} = useTheme();
  return (
    <HomeStack.Navigator
      screenOptions={{
        headerStyle: {
          backgroundColor: colors.background,
          shadowColor: colors.background, // iOS
          elevation: 0, // Android
        },
        headerTintColor: colors.text,
        headerTitleStyle: {
          fontWeight: 'bold',
        },
      }}>
      <HomeStack.Screen
        name="Home"
        component={HomeScreen}
        options={{
          title: '10gen Bank',
          headerLeft: () => (
            <View style={{marginLeft: 10}}>
              <Icon.Button
                name="log-out-outline"
                size={25}
                backgroundColor={colors.background}
                color={colors.text}
                onPress={() =>
                  navigation.reset({
                    index: 0,
                    routes: [{ name: 'LoginScreen' }],
                  })
                }
              />
            </View>
          ),
          headerRight: () => (
            <View style={{flexDirection: 'row', marginLeft: 10}}>
              <TouchableOpacity
                style={{paddingHorizontal: 10, marginTop: 5}}
                onPress={() => {
                  navigation.navigate('Profile', data);
                }}>
                <Avatar.Image
                  source={require("../assets/avatar.png")}
                  size={30}
                />
              </TouchableOpacity>
            </View>
          ),
        }}
      />
    </HomeStack.Navigator>
  );
};

const ProfileStackScreen = ({route, navigation}) => {
  const { data } = route.params;
  const {colors} = useTheme();
  console.log(data);

  return (
    <ProfileStack.Navigator
      screenOptions={{
        headerStyle: {
          backgroundColor: colors.background,
          shadowColor: colors.background, // iOS
          elevation: 0, // Android
        },
        headerTintColor: colors.text,
      }}>
      <ProfileStack.Screen
        name="Profile"
        component={ProfileScreen}
        initialParams={{ data: data }}
        options={{
          title: 'Profile',
          headerLeft: () => (
            <View style={{marginLeft: 10}}>
              <Icon.Button
                name="log-out-outline"
                size={25}
                backgroundColor={colors.background}
                color={colors.text}
                onPress={() =>
                  navigation.reset({
                    index: 0,
                    routes: [{ name: 'LoginScreen' }],
                  })
                }
              />
            </View>
          ),
          headerRight: () => (
            <View style={{marginRight: 10}}>
              <MaterialCommunityIcons.Button
                name="account-edit"
                size={25}
                backgroundColor={colors.background}
                color={colors.text}
                onPress={() => {}}
              />
            </View>
          ),
        }}
      />
    </ProfileStack.Navigator>
  );
};


const TransactionsStackScreen = ({route, navigation}) => {
  const { data } = route.params;
  const {colors} = useTheme();

  return (
    <TransactionStack.Navigator
      screenOptions={{
        headerStyle: {
          backgroundColor: colors.background,
          shadowColor: colors.background, // iOS
          elevation: 0, // Android
        },
        headerTintColor: colors.text,
      }}>
      <TransactionStack.Screen
        name="Transaction"
        component={TransactionScreen}
        initialParams={{ data: data }}
        options={{
          title: 'Payments Gateway',
          headerLeft: () => (
            <View style={{marginLeft: 10}}>
              <Icon.Button
                name="log-out-outline"
                size={25}
                backgroundColor={colors.background}
                color={colors.text}
                onPress={() =>
                  navigation.reset({
                    index: 0,
                    routes: [{ name: 'LoginScreen' }],
                  })
                }
              />
            </View>
          ),
          headerRight: () => (
            <View style={{marginRight: 10}}>
              <MaterialCommunityIcons.Button
                name="account-edit"
                size={25}
                backgroundColor={colors.background}
                color={colors.text}
                onPress={() => {}}
              />
            </View>
          ),
        }}
      />
    </TransactionStack.Navigator>
  );
};

