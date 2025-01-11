import os
import sys
import yaml
import streamlit as st

from utils import hide_st, get_list
from password import check_password
from config import CONFIG, read_config, write_config


CONFIG = read_config()

st.set_page_config(
    page_title="Advanced Bot Configuration",
    page_icon="👾",
)

hide_st(st)


def check_yaml_exists(yaml_path: str, create: bool = False) -> bool:
    folder_path, file_name = os.path.split(yaml_path)

    if not os.path.isdir(folder_path):
        if create:
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
                return True
        return False
    return True


def check_page_exists(path_to_save: str) -> str:
    folder_path, file_name = os.path.split(path_to_save)
    ext = file_name.split(".")[-1]

    i = 1
    while True:
        new_path = os.path.join(folder_path, f"page_{i}.{ext}")
        if not os.path.isfile(new_path):
            return new_path, i
        i += 1


def save_file(file_content, path_to_save: str, upload_file: bool):
    folder_path, file_name = os.path.split(path_to_save)
    if "." in file_name:
        path_to_save = folder_path

    if not os.path.exists(path_to_save):
        os.makedirs(path_to_save)

    i = 1
    mode = "w"
    path_to_save = os.path.join(folder_path, file_name)

    if path_to_save.startswith("pages"):
        path_to_save, i = check_page_exists(path_to_save)

    if upload_file:
        mode = "wb"
        path_to_save = os.path.join(folder_path, file_content.name)
        file_content = file_content.read()

    try:
        with open(path_to_save, mode) as f:
            f.write(file_content)
    except Exception as err:
        st.error(f"Please rename your file!", icon="🚨")
        print(err)
        return

    return i


def read_yaml(yaml_path: str, json: bool = False) -> str:
    if json:
        with open(yaml_path, "r") as f:
            new_datas = yaml.load(f, Loader=yaml.FullLoader)
    else:
        with open(yaml_path, 'r') as f:
            new_datas = f.read().strip()
    return new_datas


num = len(CONFIG.bots)
if check_password(st):
    st.subheader("Advanced Bot Configuration")
    if num == 0:
        st.write("There is currently no registered bot available at this time")
    else:
        bot_lists = []
        for i in range(num):
            if CONFIG.bots[i].bot_name:
                label = CONFIG.bots[i].bot_name
            else:
                label = f"Bot {i+1}"
            bot_lists.append(f"{label}")

        selected_bot = st.selectbox("Select bot", bot_lists)
        id_bot = bot_lists.index(selected_bot)

        with st.expander("New Datas"):
            yaml_path = os.path.join("bot_modules", selected_bot, "data.yaml")
            datas = ""
            if check_yaml_exists(yaml_path):
                try:
                    datas = read_yaml(yaml_path)
                except:
                    with open(yaml_path, "w") as file:
                        file.write("")
                    datas = read_yaml(yaml_path)

            yaml_file = st.text_area(
                "YAML",
                datas if datas else "",
                placeholder="Paste YAML here..."
            )

            if st.button("Save YAML"):
                check_yaml_exists(yaml_path, True)
                try:
                    with open(yaml_path, 'w') as f:
                        f.write(yaml_file)

                    CONFIG.bots[id_bot].datas = {}
                    if yaml_file == "":
                        raise ValueError("Data cleared!")

                    new_datas = read_yaml(yaml_path, True)
                    for key, value in new_datas.items():
                        CONFIG.bots[id_bot].datas.update({key: value})

                    write_config(CONFIG)
                    st.success("New data saved successfully", icon="✅")
                except ValueError as err:
                    write_config(CONFIG)
                    st.success(err, icon="✅")
                except Exception as err:
                    st.error(f"An error occured, please check your input!", icon="🚨")
                    st.error(f"Caused by: {err}", icon="🚨")

        with st.expander("New Custom File"):
            st.info("Add a new file. Additionally, you have the option to create a custom setting page for your bot here. Simply create or upload a file and locate it within the `pages` directory", icon="ℹ️")

            upload_file = False
            path_to_save_placeholder = ""
            if st.radio("New file mode", ["Create a new file", "Upload file"]) == "Create a new file":
                file_content = st.text_area(
                    "New File Content",
                    placeholder="Write or paste your text here!\nIndentation format is 4 spaces",
                    label_visibility="collapsed"
                )
                path_to_save_placeholder = "new_file.txt"
            else:
                file_content = st.file_uploader("Choose file")
                path_to_save_placeholder = "sub_folder"
                upload_file = True

            save_to = st.radio("Save as", ["Bot Modules", "Pages"])
            if save_to == "Bot Modules":
                target_path = '' if 'target_path' not in st.session_state else st.session_state[
                    'target_path']
                path_to_save = os.path.join(
                    "bot_modules", selected_bot, target_path)
                new_path = st.text_input(
                    f"Target path : {path_to_save}",
                    target_path,
                    key="target_path",
                    placeholder=path_to_save_placeholder
                )
            else:
                path_to_save = os.path.join(
                    "pages", "bot_pages", selected_bot, f"{selected_bot}.py")
                st.caption(f"Target path : {os.path.split(path_to_save)[0]}")
                st.info(
                    "Any content saved here will be displayed in the Bot Page menu", icon="ℹ️")

            if st.button("Save File"):
                if (not upload_file and file_content != "") or (upload_file and file_content is not None):
                    new_num = save_file(
                        file_content, path_to_save, upload_file)
                    if new_num:
                        CONFIG.bots[id_bot].pages.append(f"Page {new_num}")
                        write_config(CONFIG)
                        st.success(
                            f"Successfully saved to : {path_to_save}", icon="✅")
                else:
                    st.error("Unable to save an empty file!", icon="🚨")

        with st.expander("Modify Custom File"):
            choose_folder = st.radio("Select directory", ["Bot Pages", "Bot Modules"])
            pages_dir = os.path.join(os.getcwd(), "pages", "bot_pages", CONFIG.bots[id_bot].bot_name)
            module_dir = os.path.join(os.getcwd(), "bot_modules", CONFIG.bots[id_bot].bot_name)
            base_path = module_dir if choose_folder == "Bot Modules" else pages_dir
            edit_file = False
            delete_file = False

            if choose_folder == "Bot Modules":
                if os.path.exists(module_dir):
                    list_files_mod = []
                    files = os.listdir(module_dir)
                    if files:
                        for file in files:
                            if os.path.isfile(os.path.join(module_dir, file)):
                                list_files_mod.append(file)
                        selected_file = st.selectbox("Select the file you want to edit", list_files_mod)
                        edit_file = st.checkbox(f"Edit {selected_file}?")
                        delete_file = st.checkbox(f"Delete {selected_file}?")
            else:
                if os.path.exists(pages_dir):
                    list_files_page = []
                    files = os.listdir(pages_dir)
                    if files:
                        for file in files:
                            if os.path.isfile(os.path.join(pages_dir, file)):
                                list_files_page.append(file)
                        selected_file = st.selectbox("Select the file you want to edit", list_files_page)
                        edit_file = st.checkbox(f"Edit {selected_file}?")
                        delete_file = st.checkbox(f"Delete {selected_file}?")

            if edit_file:
                with open(os.path.join(base_path, selected_file)) as file:
                    read_file = file.read()
                edited_content = st.text_area("Please be aware that every changes you do here cannot be reversed", read_file, 300)

                if st.button("Save edited file"):
                    with open(os.path.join(base_path, selected_file), 'w') as file:
                        file.write(edited_content)
                    st.success("File updated!", icon="✅")
            
            if delete_file:
                st.warning("This action cannot be reversed once done.", icon="⚠️")
                if st.button("Delete file"):
                    os.system("rm " + os.path.join(base_path, selected_file))
                    st.success("File deleted!", icon="✅")

        with st.expander("Install Python Library"):
            pylib_list = get_list(st.text_area(
                "Python Library", placeholder="pyrogram\ntelethon"))
            st.caption("Write python library one item per line")
            if st.button("Install"):
                import subprocess
                try:
                    commands = [f"{sys.executable}", "-m", "pip", "install"]
                    commands.extend(pylib_list)
                    subprocess.check_call(commands)
                    st.success(
                        f"All libraries are installed successfully!", icon="✅")
                except subprocess.CalledProcessError as e:
                    st.error(
                        f"Failed to install libraries, caused by : {e}", icon="🚨")
                    
        with st.expander("Global Configs & Cookies"):
            file_content = st.file_uploader("Choose file", key='uploader cookies')
            if st.button("Upload File") and file_content is not None:
                try:
                    path_to_save = os.path.join(os.getcwd(), 'config', file_content.name)
                    save_file(file_content, path_to_save, True)
                    st.success(f"Uploaded!", icon="✅")
                except Exception as err:
                    st.error(f"Failed to upload, caused by : {err}", icon="🚨")
            

