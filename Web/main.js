
import { createClient } from 'https://cdn.jsdelivr.net/npm/@supabase/supabase-js/+esm';

const supabaseUrl = "https://njtwupjeijyfmjraycus.supabase.co/";
const supabaseKey = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5qdHd1cGplaWp5Zm1qcmF5Y3VzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NzA3NDIsImV4cCI6MjA3NTQ0Njc0Mn0.JtzbZ_qfYnChQlTBrP8d1S32KtfBXw9ltbQT8BgS8jY";
const supabase = createClient(supabaseUrl, supabaseKey);

document.addEventListener("DOMContentLoaded", () => {
  console.log("Initialization");


    const form_button = document.getElementById("form_btn");

    const form = document.querySelector("form");
    const form_input = document.getElementById("name_input");

  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const msg = form_input.value.trim();

    if (!msg) {
      alert("A mező üres, kérem adja meg a megfelelő nevet!");
      return;
    }

    try {
      const { data, error } = await supabase
        .from('visitors')
        .insert([{ user_name: msg }]);

      if (error) {
        console.error("Insert failed:", error);
        alert("Failed to send message");
      } else {
        console.log("Message sent:", data);
        alert("Üzenet elküldve!");
        form_input.value = ""; 
      }
    } catch (err) {
      console.error("Unexpected error:", err);
      alert("An unexpected error occurred");
    }
  });
});



