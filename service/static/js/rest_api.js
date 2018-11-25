$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        //$("#_id").val(res.id);
        //$("#pet_name").val(res.name);
        $("first_name").val(res.first_name);
        //$("#pet_category").val(res.category);
        $("#pet_name").val(res.name);
        if (res.available == true) {
            $("#pet_available").val("true");
        } else {
            $("#pet_available").val("false");
        }
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#pet_name").val("");
        $("#pet_category").val("");
        $("#pet_available").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // Create a Pet
    // ****************************************

    $("#create-btn").click(function () {

        var first_name = $("#first_name").val();
        var last_name = $("#last_name").val();
        var address = $("#address").val();
        var email = $("#email").val();
        var username = $("#username").val();
        var password = $("#password").val();
        var phone_number = $("#phone_number").val();
        var active = $("#active").val() == "true";

        var data = {
            "first_name": first_name,
            "last_name": last_name,
            "address": address,
            "email": email,
            "username": username,
            "password": password,
            "phone_number": phone_number,
            "active": active
        };

        var ajax = $.ajax({
            type: "POST",
            url: "/customers",
            contentType:"application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });


    // ****************************************
    // Update a Pet
    // ****************************************

    $("#update-btn").click(function () {

        var pet_id = $("#pet_id").val();
        var name = $("#pet_name").val();
        var category = $("#pet_category").val();
        var available = $("#pet_available").val() == "true";

        var data = {
            "name": name,
            "category": category,
            "available": available
        };

        var ajax = $.ajax({
                type: "PUT",
                url: "/customers/" + pet_id,
                contentType:"application/json",
                data: JSON.stringify(data)
            })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Retrieve a Pet
    // ****************************************

    $("#retrieve-btn").click(function () {

        var pet_id = $("#pet_id").val();

        var ajax = $.ajax({
            type: "GET",
            url: "/customers/" + pet_id,
            contentType:"application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Delete a Pet
    // ****************************************

    $("#delete-btn").click(function () {

        var customers_id = $("#id").val();

        flash_message("Customer with id:" + customers_id + "with Delete")

        var ajax = $.ajax({
            type: "DELETE",
            url: "/customer/" + customers_id,
            contentType:"application/json",
            data: '',
        })

        ajax.done(function(res){
            clear_form_data()
            flash_message("Customer with ID [" + res.id + "] has been Deleted!")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });

    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#pet_id").val("");
        clear_form_data()
    });

    // ****************************************
    // Search for a Pet
    // ****************************************

    $("#search-btn").click(function () {

        var first_name = $("#first_name").val();
        var last_name = $("#last_name").val();
        var address = $("#address").val();
        var email = $("#email").val();
        var username = $("#username").val();
        var password = $("#password").val();
        var phone_number = $("#phone_number").val();
        var active = $("#active").val() == "true";

        var queryString = ""

        if (first_name) {
            queryString += 'first_name=' + name
        }
        if (last_name) {
            if (queryString.length > 0) {
                queryString += '&last_name' + last_name
            } else {
                queryString += 'last_name=' + last_name
            }
        }
        if (address) {
            if (queryString.length > 0) {
                queryString += 'address=' + address
            } else {
                queryString += 'address=' + address
            }
        }
        if (email) {
            if (queryString.length > 0) {
                queryString += '&email' + email
            } else {
                queryString += 'email=' + email
            }
        }
        if (username) {
            if (queryString.length > 0) {
                queryString += '&username' + username
            } else {
                queryString += 'username=' + username
            }
        }
        if (password) {
            if (queryString.length > 0) {
                queryString += '&password' + password
            } else {
                queryString += 'password=' + password
            }
        }
        if (phone_number) {
            if (queryString.length > 0) {
                queryString += '&phone_number' + phone_number
            } else {
                queryString += 'phone_number=' + phone_number
            }
        }
        /*if (active && active != "true") {
            if (queryString.length > 0) {
                queryString += '&active=' + active
            } else {
                queryString += 'active=' + active
            }
        }*/

        if (queryString.length > 0){
            var ajax = $.ajax({
                type: "GET",
                //url: "/customers?" + queryString,

                url: "/customers?" + queryString,
                //url: "/customers?address=USA",
                contentType:"application/json",
                data: ''
            })
        }
        else{
            var ajax = $.ajax({
                type: "GET",
                //url: "/customers?" + queryString,

                url: "/customers",
                contentType:"application/json",
                data: ''
            })
        }


        ajax.done(function(res){
            //alert(res.toSource())
            $("#search_results").empty();
            $("#search_results").append('<table class="table-striped">');
            var header = '<tr>'
            header += '<th style="width:10%">first_name</th>'
            header += '<th style="width:10%">last_name</th>'
            header += '<th style="width:10%">address</th>'
            header += '<th style="width:10%">email</th>'
            header += '<th style="width:10%">username</th>'
            header += '<th style="width:10%">password</th>'
            header += '<th style="width:10%">phone_number</th>'
            header += '<th style="width:10%">active</th></tr>'

            $("#search_results").append(header);
            for(var i = 0; i < res.length; i++) {
                customer = res[i];
                var row = "<tr><td>"+customer.first_name+"</td><td>"
                                    +customer.last_name+"</td><td>"
                                    +customer.address+"</td><td>"
                                    +customer.email+"</td></tr>"
                                    +customer.username+"</td></tr>"
                                    +customer.password+"</td></tr>"
                                    +customer.phone_number+"</td></tr>"
                                    +customer.active+"</td></tr>"
                                    ;
                $("#search_results").append(row);
            }

            $("#search_results").append('</table>');

            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

})
