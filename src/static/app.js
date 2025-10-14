document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities", {
        cache: 'no-cache'
      });
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";
      
      // Clear activity select dropdown (keep the default option)
      activitySelect.innerHTML = '<option value="">-- Select an activity --</option>';

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;

        // Create participants list HTML
        let participantsHtml = '';
        if (details.participants && details.participants.length > 0) {
          const participantsList = details.participants.map(email => {
            // Extract name from email (part before @)
            const studentName = email.split('@')[0].replace(/\./g, ' ').replace(/(\b\w)/gi, (match) => match.toUpperCase());
            return `
              <div class="participant-item" data-activity="${name}" data-email="${email}">
                <span class="participant-name">${studentName}</span>
                <button class="delete-participant" title="Remove participant" aria-label="Remove ${studentName}">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M18 6 L6 18 M6 6 l12 12"></path>
                  </svg>
                </button>
              </div>
            `;
          }).join('');
          
          participantsHtml = `
            <div class="participants-section">
              <p class="participants-header"><strong>Current Participants:</strong></p>
              <div class="participants-list">
                ${participantsList}
              </div>
            </div>
          `;
        } else {
          participantsHtml = `
            <div class="participants-section">
              <p class="participants-header"><strong>Current Participants:</strong></p>
              <p class="no-participants">No participants yet - be the first to join!</p>
            </div>
          `;
        }

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          ${participantsHtml}
        `;

        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });

      // Add event listeners for delete buttons
      addDeleteEventListeners();
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Function to add event listeners to delete buttons
  function addDeleteEventListeners() {
    const deleteButtons = document.querySelectorAll('.delete-participant');
    deleteButtons.forEach(button => {
      button.addEventListener('click', async (event) => {
        event.preventDefault();
        const participantItem = event.target.closest('.participant-item');
        const activityName = participantItem.dataset.activity;
        const email = participantItem.dataset.email;
        const studentName = participantItem.querySelector('.participant-name').textContent;
        
        if (confirm(`Are you sure you want to remove ${studentName} from ${activityName}?`)) {
          await unregisterParticipant(activityName, email);
        }
      });
    });
  }

  // Function to unregister a participant from an activity
  async function unregisterParticipant(activityName, email) {
    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activityName)}/participants/${encodeURIComponent(email)}`,
        {
          method: "DELETE",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        // Refresh activities to show updated participant list
        fetchActivities();
      } else {
        messageDiv.textContent = result.detail || "Failed to remove participant";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to remove participant. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error removing participant:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
        // Refresh activities to show updated participant list
        fetchActivities();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  fetchActivities();
});
