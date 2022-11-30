import { async_post_request } from './utils.js'

$( document ).ready(async function() {
    await create_submission_listener();
});


function display_results(str_to_post) {
    document.getElementById("categorized-display").value = str_to_post;
}

async function create_submission_listener()  {
    $("#submit-info").click(async function () {
        const url = "/submit_info";
        const category_serial = document.getElementById("category-data")
        const category_serial_list = category_serial.value.split("\n");
        const notes_serial = document.getElementById("notes")
        const notes_serial_list = notes_serial.value.split("\n");

        console.log(`category_serial_list = ${category_serial_list}`)
        console.log(`notes_serial_list = ${notes_serial_list}`)

        // Wait for the categories and notes to be processed
        const data_json = {
            "category_info": category_serial_list,
            "notes": notes_serial_list
        }

        const processed_res = await async_post_request(url, data_json);
        display_results(processed_res);
    });

}
