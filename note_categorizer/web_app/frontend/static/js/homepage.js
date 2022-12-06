import { async_post_request } from './utils.js'

$( document ).ready(async function() {
    await create_submission_listener();
    await create_uncategorized_update_submission_listener();

});


function display_results(str_to_post) {
    const output_text_area = document.getElementById("categorized-display");
    output_text_area.value = str_to_post;
}

/**
 * After adding to the page, the size of the Category List / Notes List
 * is very small. Resize them.
 */
function resize_input_boxes() {
    const category_list = document.getElementById("category-data");
    const note_list = document.getElementById("notes");
    const output_box = document.getElementById("categorized-display");

    category_list.style.height = 'auto';
    category_list.style.height = category_list.scrollHeight + 'px';

    note_list.style.height = 'auto';
    note_list.style.height = note_list.scrollHeight + 'px';

    output_box.style.height = 'auto';
    output_box.style.height = output_box.scrollHeight + 'px';

}

/**
 * @brief Creates the row (of 2 columns) for the current uncategorized note
 * @param {Array[string]} category_list - The list of all valid categories to select
 * @param {string} uncategorized_note - The uncategorized note to ask about
 * @param {int} note_idx - The number note being asked baout
 * @return {HTMLDivElement} The div representing the row for the current prompt
 * @note Create in the form:
 * ```html
        <div class="row box" id="uncategorized-note-row-idx">
            <div class="columns" id="uncategorized-note-idx">
                <div class="column has-text-left">
                    <!-- uncategorized note -->
                </div>
                <div id="dropdown-menus-num" class="column">
                    <!-- dropdown for category -->
                </div>
            </div>
        </div>
 * ```
 */
function create_uncategorized_prompt_row(category_list, uncategorized_note, note_idx) {
    const columns_el = document.createElement("div");
    columns_el.classList.add("columns");
    columns_el.setAttribute("id", `uncategorized-note-${note_idx}`);

    const note_column_el = create_uncategorized_label_column(uncategorized_note);
    const dropdown_column_el = create_dropdown_column(category_list, note_idx);
    columns_el.appendChild(note_column_el);
    columns_el.appendChild(dropdown_column_el);

    const row_el = document.createElement("div");
    row_el.classList.add("row");
    row_el.classList.add("box");
    row_el.setAttribute("id", `uncategorized-note-row-${note_idx}`);
    row_el.appendChild(columns_el);

    return row_el;
}

/**
 *
 * @param {string} note_str The note being asked about
 * @return {HTMLDivElement} A div element containing the note in text
 *
 */
function create_uncategorized_label_column(note_str) {
    const note_column = document.createElement("div");
    note_column.classList.add("column");
    note_column.classList.add("has-text-left");
    note_column.textContent = note_str;

    return note_column;
}

/**
 * @brief
 * Function to create a dropdown for 1 uncategorized note.
 * Places the drop down after the previous.
 * The dropdown enables users to select the correct category associated with
 * the note.
 * @return {HTMLDivElement} An element representing the bulma select class
 * @note Of the form:
 * ```html
 * <div class="select is-info" id="menu-id">
 *        <select>
 *        <option value="" disabled selected>Select the category</option>
 *        <option>option1</option>
 *        <option>option2</option>
 *        <option>option3</option>
 *        </select>
 * </div>
 * ```
 */
function create_dropdown_column(category_list, menu_idx) {

    // create parent
    const selection_menu = document.createElement("div");
    selection_menu.classList.add("select");
    selection_menu.classList.add("is-info");
    selection_menu.setAttribute("id", `uncategorized-${menu_idx}`);

    // create selection wrapper
    const select_el = document.createElement("select");

    const placeholder_option = document.createElement("option");
    placeholder_option.value = "";
    placeholder_option.disabled = true;
    placeholder_option.selected = true;
    placeholder_option.textContent = "Select the category";
    select_el.appendChild(placeholder_option);

    // create and add all category options to the selection tag
    category_list.forEach(element => {
        const option_el = document.createElement("option")
        option_el.textContent = element;
        select_el.appendChild(option_el);
    });

    selection_menu.appendChild(select_el);
    return selection_menu

}

/**
 * Displays the output box containing the uncategorized
 * @param uncategorized_list = List of uncategorized notes
 * @param {Array[string]} uncategorized_note_list The list of uncategorized notes
 */
function display_uncategorized_input(uncategorized_note_list, category_list) {
    // document.getElementById("uncategorized-wrapper").hidden = false;
    document.getElementById("uncategorized-wrapper").classList.remove("is-hidden")
    const uncategorized_rows_el = document.getElementById("uncategorized-row-container");

    uncategorized_note_list.forEach((uncategorized_note, idx) => {
        const row_el = create_uncategorized_prompt_row(category_list, uncategorized_note, idx);
        uncategorized_rows_el.appendChild(row_el)
    })

}

/**
 * @brief Hides the uncategorized input section and removes all of its dropdowns
 */
function hide_remove_uncategorized_input() {
    // document.getElementById("uncategorized-wrapper").hidden = true;
    document.getElementById("uncategorized-wrapper").classList.add("is-hidden");
    const uncategorized_rows_el = document.getElementById("uncategorized-row-container");
    while (uncategorized_rows_el.firstChild) {
        uncategorized_rows_el.removeChild(uncategorized_rows_el.firstChild);
    }
}


/**
 * @brief Handle the server response after processing the data
 */
function handle_response_after_processing(processed_res) {
    const output_res = processed_res["processed_data"]
    if (output_res == "") {
        return
    }

    const are_uncategorized = processed_res["are_uncategorized"]
    if (are_uncategorized == true) {
        display_uncategorized_input(processed_res["uncategorized_list"],
            processed_res["category_list"]
        )
    }
    else {
        hide_remove_uncategorized_input()
    }
    display_results(output_res);

    resize_input_boxes();
}

async function create_submission_listener()  {
    $("#submit-info").click(async function () {
        const url = "/submit_info";
        const category_serial = document.getElementById("category-data")
        const category_serial_list = category_serial.value.split("\n");
        const notes_serial = document.getElementById("notes")
        const notes_serial_list = notes_serial.value.split("\n");

        // Wait for the categories and notes to be processed
        const data_json = {
            "category_info": category_serial_list,
            "notes": notes_serial_list
        }

        const processed_res = await async_post_request(url, data_json);
        handle_response_after_processing(processed_res)
    });
}

async function create_uncategorized_update_submission_listener() {
    $("#submit-uncategorized-update").click(async function () {
        const url = "/submit_uncategorized_update";

        let data_json = {};

        // Check each row to see if they selected a category
        Array.from($("#uncategorized-row-container").children()).forEach(row_el => {
            const selected_category = get_dropdown_selection_from_row(row_el);
            // Only update for notes that had a selection get made
            if (selected_category != null) {
                const note_text = get_note_str_from_row(row_el);
                data_json[note_text] = selected_category;
            }
        });

        console.log(data_json)

        // Wait for the note updates to be processed
        hide_remove_uncategorized_input();
        const processed_res = await async_post_request(url, data_json);
        console.log(processed_res)
        handle_response_after_processing(processed_res);
    });
}

/**
 * @return {String | null}
 * * The Category string selected by the dropdown in the given row
 * * Null if nothing is selected
 * @param {HTMLDivElement} row_el The row to get the selection from
 */
function get_dropdown_selection_from_row(row_el) {
    const select_el = row_el.querySelector("select");
    const selected = select_el.options[select_el.selectedIndex];
    if(selected.disabled == true) {
        return null;
    } else{
        return selected.text;
    }
}

/**
 * @return {String}
 * * The note in String form for the given row
 * @param {HTMLDivElement} row_el The row to get the selection from
 */
function get_note_str_from_row(row_el) {
    const note_tag = row_el.querySelector(".column.has-text-left");
    return note_tag.textContent;
}
