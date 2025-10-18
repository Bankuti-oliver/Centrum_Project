const supabaseUrl = "";
const supabaseKey = "";
const supabase = supabase.createClient(supabaseUrl, supabaseKey);




console.log("Initialization");

const form_button = document.getElementById("form_btn")

form_button.addEventListener("click", export_data)

function export_data(){
    
}