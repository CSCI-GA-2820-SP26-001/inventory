$(function () {
  $("#clear-btn").click(function () {
    $("#inventory_id").val("");
    $("#inventory_name").val("");
    $("#inventory_product_id").val("");
    $("#inventory_quantity").val("");
    $("#inventory_condition").val("");
    $("#flash_message").text("Form cleared");
  });

  $("#create-btn").click(function () {
    $("#flash_message").text("Create button clicked");
  });

  $("#retrieve-btn").click(function () {
    $("#flash_message").text("Retrieve button clicked");
  });

// ****************************************
// Update an Inventory Item
// ****************************************

$("#update-btn").click(function () {

    let inventory_id = $("#inventory_id").val();
    let name = $("#inventory_name").val();
    let product_id = $("#inventory_product_id").val();
    let quantity_on_hand = parseInt($("#inventory_quantity").val());
    let condition = $("#inventory_condition").val();

    let data = {
        "name": name,
        "product_id": product_id,
        "quantity_on_hand": quantity_on_hand,
        "condition": condition
    };

    $("#flash_message").empty();

    let ajax = $.ajax({
        type: "PUT",
        url: `/inventory/${inventory_id}`,  
        contentType: "application/json",
        data: JSON.stringify(data)
    });

    ajax.done(function(res){
        update_form_data(res);
        flash_message("Success");
    });

    ajax.fail(function(res){
        flash_message(res.responseJSON.message);
    });

});

function update_form_data(res) {
    $("#inventory_id").val(res.id);
    $("#inventory_name").val(res.name);
    $("#inventory_product_id").val(res.product_id);
    $("#inventory_quantity").val(res.quantity_on_hand);  
    $("#inventory_condition").val(res.condition);
}

  $("#delete-btn").click(function () {
    $("#flash_message").text("Delete button clicked");
  });

  $("#list-btn").click(function () {
    $("#flash_message").text("List button clicked");
  });

  $("#query-btn").click(function () {
    $("#flash_message").text("Query button clicked");
  });

  $("#action-btn").click(function () {
    $("#flash_message").text("Action button clicked");
  });
});