import axios from "axios";

const thymeClient = axios.create({
  baseURL: "http://localhost:8000/api", // Change to your API base URL
  timeout: 10000,
  headers: {
    "Content-Type": "application/json",
  },
});

thymeClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Server responded with a status other than 2xx
      console.error("API Error:", error.response.status, error.response.data);
    } else if (error.request) {
      // No response received
      console.error("No response from API:", error.request);
    } else {
      // Something else happened
      console.error("Error:", error.message);
    }
    return Promise.reject(error);
  }
);

export default thymeClient;
