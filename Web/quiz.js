    document.getElementById("scan-btn").addEventListener("click", () => {
      fetch("/read_nfc")
        .then(res => res.json())
        .then(data => {
          if (data.error) {
            document.getElementById("result").innerText = "Hiba: " + data.error;
            return;
          }

          const scannedName = data.user_name.trim().toLowerCase();
          const expectedName = currentAnimal.toLowerCase();

          if (scannedName === expectedName) {
            document.getElementById("result").innerText = "Helyes! Ez egy " + scannedName;
          } else {
            document.getElementById("result").innerText = ` Helytelen! Ez nem ${expectedName}, hanem ${scannedName}`;
          }
        })
        .catch(err => {
          console.error(err);
          document.getElementById("result").innerText = "hiba!";
        });
    });