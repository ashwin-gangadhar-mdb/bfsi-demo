import axios from 'axios';

class RESTProvider {
  constructor() {
  }

  get(endpoint) {
    return axios.get(endpoint);
  }

  post(endpoint, data) {
    return axios.post(endpoint, data);
  }

  put(endpoint, data) {
    return axios.put(endpoint, data);
  }

  delete(endpoint) {
    return axios.delete(endpoint);
  }
}

export default new RESTProvider();
