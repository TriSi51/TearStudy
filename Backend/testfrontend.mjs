import axios from 'axios';
const fs = require('fs');
const FormData = require('form-data');
const fetch = require('node-fetch');
const mime = require('mime-types'); // Ensure you have mime-types installed
const sendMessage = async (message) => {
  try {
    const response = await axios.post('http://127.0.0.1:8000/message', {
      message: message
    });

    // Log the entire response object to see all the details
    console.log('Full Response:', response);
    console.log('Message:', response.data.message);

  } catch (error) {
    console.error('Error Response:', error.response ? error.response.data : error.message);
  }
};


// Function to fake the file upload
async function fakeUpload(filePath) {
  const form = new FormData();

  // Automatically determine the file type from the file extension
  const fileType = mime.lookup(filePath);

  // Append the file to the form data
  form.append('file', fs.createReadStream(filePath));
  form.append('file_type', fileType); // Now automatically derived

  // Send the file to the backend
  const response = await fetch('http://localhost:8000/uploadfile/', {
      method: 'POST',
      body: form
  });

  const result = await response.json();
  console.log(result);
}

// Example usage
fakeUpload('/home/ngotrisi/Data_Analyst_project/Backend/train.csv');
