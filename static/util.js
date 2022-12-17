const form = document.getElementById("form");
if (form != null) {
    form.addEventListener("submit", payNow);
}

function payNow(e) {
    e.preventDefault();

    FlutterwaveCheckout({
        public_key: "FLWPUBK_TEST-e61590805f79c3be682dec246f8c1510-X",
        tx_ref: "AK_" + Math.floor(Math.random() * 1000000000 + 1),
        amount: document.getElementById(amount).value,
        currency: "RWF",

        //payment_options: "card,mobilemoney,ussd",

        customer: {
            email: document.getElementById("email").value,
            phonenumber: document.getElementById("mobile").value,
            name: document.getElementById("name").value,
            amount: document.getElementById("amount").value,
        },

        callback: (data) => {
            const reference = data.tx_ref;
            alert("Payment complete! Reference: " + reference);
        },

        customizations: {
            title: "IHAME App",
            description: "FlutterWave Integration in Javascript.",
            logo: "C:\\Users\\IHAME\\Desktop\\WebDesign\\IhameWebsite\\design\\20211128_231345_0000.png",
        },
    });
}
