/**
 * Google Apps Script to connect Google Form to SlackChannelCreator FastAPI
 * 
 * Instructions:
 * 1. Open your Google Form: https://forms.gle/fZxPguP1swhQDnmC6
 * 2. Click 3 dots → Script editor
 * 3. Replace default code with this script
 * 4. Update YOUR_FASTAPI_URL with your actual URL
 * 5. Save and run setupTrigger() once
 */

// ⚠️ IMPORTANT: Replace this with your actual FastAPI URL
const FASTAPI_URL = 'https://login.theccdocs.com:8443/custom/gateway/gateway.php/forms/webhook';
// For local testing: 'http://localhost:9000/forms/webhook'

/**
 * Main function triggered when form is submitted
 */
function onFormSubmit(e) {
  try {
    // Log the form response for debugging
    console.log('Form submitted:', e.values);
    
    // Extract form values - adjust indices based on your form field order
    const formData = {
      channel_name: e.values[1], // Assuming channel name is 2nd question
      requester_email: e.values[2], // Assuming email is 3rd question  
      requester_name: e.values[3], // Assuming name is 4th question (optional)
      visibility: e.values[4] ? e.values[4].toLowerCase() : 'public', // Assuming visibility is 5th question
      users_to_add: e.values[5] ? e.values[5].split(',').map(email => email.trim()) : [], // Assuming users is 6th question
      form_submission_id: e.response.getId() // Google Form submission ID
    };
    
    console.log('Sending data to FastAPI:', formData);
    
    // Send POST request to FastAPI webhook
    const response = UrlFetchApp.fetch(FASTAPI_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      payload: JSON.stringify(formData)
    });
    
    // Log response for debugging
    console.log('FastAPI Response:', response.getContentText());
    
    if (response.getResponseCode() === 200) {
      console.log('✅ Channel creation request sent successfully');
    } else {
      console.error('❌ Error from FastAPI:', response.getContentText());
    }
    
  } catch (error) {
    console.error('❌ Script error:', error.toString());
    
    // Optional: Send error notification email
    // GmailApp.sendEmail('your-email@domain.com', 'Form Script Error', error.toString());
  }
}

/**
 * Set up the form submit trigger - run this function once manually
 */
function setupTrigger() {
  try {
    // Delete existing triggers to avoid duplicates
    const triggers = ScriptApp.getProjectTriggers();
    triggers.forEach(trigger => {
      if (trigger.getHandlerFunction() === 'onFormSubmit') {
        ScriptApp.deleteTrigger(trigger);
      }
    });
    
    // Create new trigger
    const form = FormApp.getActiveForm();
    ScriptApp.newTrigger('onFormSubmit')
      .forForm(form)
      .onFormSubmit()
      .create();
      
    console.log('✅ Trigger set up successfully');
    
  } catch (error) {
    console.error('❌ Error setting up trigger:', error.toString());
  }
}

/**
 * Test function to manually test the webhook
 */
function testWebhook() {
  const testData = {
    channel_name: 'test-channel',
    requester_email: 'test@example.com',
    requester_name: 'Test User',
    visibility: 'public',
    users_to_add: ['user1@example.com', 'user2@example.com'],
    form_submission_id: 'test-submission-' + Date.now()
  };
  
  try {
    const response = UrlFetchApp.fetch(FASTAPI_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      payload: JSON.stringify(testData)
    });
    
    console.log('Test response:', response.getContentText());
  } catch (error) {
    console.error('Test error:', error.toString());
  }
} 