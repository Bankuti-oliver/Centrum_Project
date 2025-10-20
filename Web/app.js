async function kuldes() {
    const form = document.getElementById("Form_1");
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());

    const response = await fetch("https://centrum.1percprogramozas.hu/api/iras", {
        method: "POST",
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data),
    })

    if (!response.ok) throw new Error(`Error: ${response.statusText}`);

    const result = await response.json();
    console.log('Success:', result);
    const valasz = document.getElementById("valasz");
    valasz.innerHTML = result.msg;
    console.log(result.msg);
    

    

}





