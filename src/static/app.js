document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";
      // Reset activity select so options don't accumulate on re-load
      activitySelect.innerHTML = '<option value="">-- Select an activity --</option>';

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
        `;

        // Participants section (bulleted list with small avatars)
        const participantsDiv = document.createElement('div');
        participantsDiv.className = 'participants';
        const title = document.createElement('strong');
        title.textContent = 'Participants:';
        participantsDiv.appendChild(title);

        const ul = document.createElement('ul');
        if (details.participants && details.participants.length > 0) {
          details.participants.forEach((pEmail) => {
            const li = document.createElement('li');
            li.className = 'participant-item';

            const avatar = document.createElement('span');
            avatar.className = 'avatar';
            const namePart = (pEmail || '').split('@')[0] || '';
            const initials = namePart
              .split(/[\._-]+/)
              .map(s => s && s[0])
              .filter(Boolean)
              .join('')
              .slice(0, 2)
              .toUpperCase();
            avatar.textContent = initials || 'S';

            const nameSpan = document.createElement('span');
            nameSpan.className = 'participant-name';
            nameSpan.textContent = pEmail;

            li.appendChild(avatar);
            li.appendChild(nameSpan);
            ul.appendChild(li);
          });
        } else {
          const none = document.createElement('p');
          none.className = 'no-participants';
          none.textContent = 'No participants yet';
          participantsDiv.appendChild(none);
        }

        if (ul.children.length) participantsDiv.appendChild(ul);

        activityCard.appendChild(participantsDiv);

        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
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
