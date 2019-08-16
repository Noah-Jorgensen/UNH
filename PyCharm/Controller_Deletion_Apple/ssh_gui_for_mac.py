# Created by Noah Jorgensen
# 6/7/19

import re
from pathlib import Path
import csv
import netmiko
import tkinter
from tkinter import messagebox
from tkinter import filedialog
from tkinter import ttk


def select():
    # check if mac is valid / clean up bad macs
    invalid_mac = False
    if deletionVar.get() != "":
        if dropOption.get() == "MAC Address":
            invalid_mac = fix_mac(invalid_mac)
    else:
        selectedVarLabel2.config(text="NONE SELECTED")

    # make selection on screen, making sure the mac is valid
    if deletionVar.get() != "" and not invalid_mac:
        selectedVarLabel2.config(text=deletionVar.get())
    else:
        selectedVarLabel2.config(text="NONE SELECTED")

    selectedTypeLabel2.config(text=dropOption.get())


def fix_mac(not_valid):
    if (len(deletionVar.get()) > 17) or (len(deletionVar.get()) < 12):
        messagebox.showinfo("Incorrect MAC Format", "Incorrect MAC Address format: '" + deletionVar.get() + "'\n"
                            "Make sure no extra spaces were included by accident.", icon="error")
        not_valid = True
        return not_valid
    elif re.match("^([0-9A-Fa-f]{2}[:]){5}([0-9A-Fa-f]{2})$", deletionVar.get()):
        # CORRECT MAC USED
        upper = deletionVar.get()
        upper = upper.upper()
        deletionVar.set(upper)
        return not_valid
    elif re.match("^([0-9A-Fa-f]{2}[-]){5}([0-9A-Fa-f]{2})$", deletionVar.get()):
        # replace the -'s with :'s
        fix = deletionVar.get()
        fix = fix.replace("-", ":")
        fix = fix.upper()
        deletionVar.set(fix)
        return not_valid
    elif re.match("^([0-9A-Fa-f]{12})$", deletionVar.get()):
        # only 12 characters provided, add in the :'s
        fix = deletionVar.get()
        fix = ":".join(fix[i:i + 2] for i in range(0, len(fix), 2))
        fix = fix.upper()
        deletionVar.set(fix)
        return not_valid
    else:
        # incorrect mac used
        messagebox.showinfo("Incorrect MAC Format", "Incorrect MAC Address format: '" + deletionVar.get() + "'\n"
                            "Make sure no extra spaces were included by accident.", icon="error")
        not_valid = True
        return not_valid


def delete():
    if selectedVarLabel2.cget("text") != "NONE SELECTED":
        result = messagebox.askquestion("DELETE", "Are you sure you want to delete the " +
                                        selectedTypeLabel2.cget("text") + ' "' +
                                        selectedVarLabel2.cget("text") + '"? \n\nBy choosing "Yes" an SSH connection '
                                                                         'will be made to the controllers.'
                                                                         '\n\nNOTE: THE ENTIRE PROCESS WILL TAKE '
                                                                         'ABOUT 5-10 SECONDS ON AVERAGE.'
                                                                         , icon='warning')
        if result == 'yes':
            if len(activeList) > 0:
                ssh_connect()
            else:
                messagebox.showinfo("Controller Error", "There are currently no hostnames in the hostnames list. "
                                                        "You can add hostnames by going to the "
                                                        "settings tab.", icon='error')
    else:
        messagebox.showinfo("DELETE", "You have not specified anything to delete", icon='error')


def ssh_connect():
    grab_var = selectedVarLabel2.cget("text")
    grab_type = selectedTypeLabel2.cget("text")
    final_response = ""
    del responses[:]  # make sure previous list is gone before proceeding

    for hostname in activeList:
        try:
            controller = netmiko.ConnectHandler(ip=hostname.rstrip(), device_type="aruba_os",
                                                username="api-login", password="Arub@08!", secret="Password1")
        except netmiko.ssh_exception.NetMikoTimeoutException:
            messagebox.showinfo("SSH Failure", "SSH connection to '" + hostname + "' timed out. You may not "
                                               "be connected to the UNH admin network, or the hostname "
                                               "provided is invalid.",
                                icon="error")
            return
        except netmiko.ssh_exception.AuthenticationException:
            messagebox.showinfo("SSH Failure", "SSH connection to '" + hostname + "' failed. "
                                                                                  "Incorrect username/password"
                                                                                  " was entered.",
                                icon="error")
            return

        except ValueError:
            messagebox.showinfo("SSH Failure", "SSH connection to '" + hostname + "' failed. An incorrect "
                                                                                  "value was used. "
                                                                                  "Make sure 'device_type' "
                                                                                  "and 'secret' are correct.",
                                icon="error")
            return

        if grab_type == "Username":
            output = controller.send_command("aaa user delete name " + grab_var)
            responses.append(hostname + ": " + output)
        elif grab_type == "MAC Address":
            output = controller.send_command("aaa user delete mac " + grab_var)
            responses.append(hostname + ": " + output)
        elif grab_type == "IP Address":
            output = controller.send_command("aaa user delete " + grab_var)
            responses.append(hostname + ": " + output)

        controller.disconnect()

    final_response = final_response + "Controller Responses:\n\n"
    for response in responses:
        final_response = final_response + response
    messagebox.showinfo("Finished", final_response)


def ask_for_file():
    file = filedialog.askopenfile(parent=mainWindow, mode='rb', title='Choose CSV File',
                                  filetypes=(("csv files", "*.csv"), ("all files", "*.*")))

    if file is not None:
        extension = Path(file.name).resolve().suffix
        if extension == ".csv":
            csvVar.set(file.name)
        else:
            csvVar.set("")
            messagebox.showinfo("Incorrect File Type", "Please make sure to choose a '.csv' file.", icon="error")
    else:
        csvVar.set("")
        selectedCSVLabel2.config(text="NONE SELECTED")
        csv_full_deletionVar.set("NONE SELECTED")  # this is important to keep track of what was previously selected


def fill_mac_list():
    # make sure file ends in .csv right here
    last_four = csvEntry.get()[-4:]  # should be .csv

    if csvEntry.get() != "" and last_four == ".csv":
        filename = Path(csvEntry.get()).resolve().stem
        extension = Path(csvEntry.get()).resolve().suffix
        selectedCSVLabel2.config(text=filename + extension)
        csv_full_deletionVar.set(csvEntry.get())  # this is important to keep track of what was previously selected

        del mac_list_master[:]  # this will remove the previous selected items from the last SELECTed file
        del broken_macs[:]  # make sure to also remove all of the previously selected broken mac addresses

        try:
            with open(csvEntry.get(), 'r', encoding='utf-8-sig') as csv_file:
                csv_reader = csv.reader(csv_file)

                for line in csv_reader:
                    for item in line:
                        if item != "":
                            mac_list_master.append(item)

        except FileNotFoundError:
            selectedCSVLabel2.config(text="NONE SELECTED")
            csv_full_deletionVar.set("NONE SELECTED")  # this is important to keep track of what was previously selected

        # need to check to see if the mac list is empty here
        if not mac_list_master:
            messagebox.showinfo("Invalid CSV", "The provided CSV file appears to be empty. Make sure to provide "
                                               "MAC Addresses in the file."
                                             , icon='error')
            selectedCSVLabel2.config(text="NONE SELECTED")
            return

        # now that we know the list isn't empty, we need to fix up the macs
        fix_mac_csv()

        # make sure that not all of the macs in the file were invalid
        if not mac_list_master:
            messagebox.showinfo("Invalid CSV", "The CSV file provided did not contain any readable MAC Addresses. "
                                               "Make sure you are entering MAC Addresses only, and that they are "
                                               "formatted correctly."
                                             , icon='error')
            selectedCSVLabel2.config(text="NONE SELECTED")
            return

    elif csvEntry.get() != "" and last_four != ".csv":
        selectedCSVLabel2.config(text="NONE SELECTED")
    else:
        selectedCSVLabel2.config(text="NONE SELECTED")


def delete_csv():
    if csv_full_deletionVar.get() != "NONE SELECTED":
        filename = Path(csv_full_deletionVar.get()).resolve().stem
        extension = Path(csv_full_deletionVar.get()).resolve().suffix
        result = messagebox.askquestion("DELETE", 'Are you sure you want to delete the MAC Addresses listed in the '
                                                  'CSV file '
                                                  '"' + filename + extension + '"?'
                                                  '\n\nBy choosing "Yes" an SSH connection '
                                                  'will be made to the controllers.'
                                                  '\n\nNOTE: THE ENTIRE PROCESS WILL TAKE ABOUT '
                                                  '5-30 SECONDS DEPENDING ON HOW MANY MAC ADDRESSES '
                                                                               'ARE BEING SENT TO THE CONTROLLER.'
                                                , icon='warning')
        if result == 'yes':
            if len(activeList) > 0:
                ssh_connect_csv()
            else:
                messagebox.showinfo("Controller Error", "There are currently no hostnames in the hostnames list. "
                                                        "You can add hostnames by going to the "
                                                        "settings tab.", icon='error')
    else:
        messagebox.showinfo("DELETE FROM CSV", "You have not specified a valid CSV file to delete MAC Addresses with"
                            , icon='error')


def fix_mac_csv():
    indexes_for_deletion = []

    for index, item in enumerate(mac_list_master):
        if (len(item) > 17) or (len(item) < 12):
            broken_macs.append(item)
            indexes_for_deletion.append(index)  # make sure this index isn't used
            continue
        elif re.match("^([0-9A-Fa-f]{2}[:]){5}([0-9A-Fa-f]{2})$", item):
            # CORRECT MAC USED
            upper = item
            upper = upper.upper()
            mac_list_master[index] = upper
            continue
        elif re.match("^([0-9A-Fa-f]{2}[-]){5}([0-9A-Fa-f]{2})$", item):
            # replace the -'s with :'s
            fix = item
            fix = fix.replace("-", ":")
            fix = fix.upper()
            mac_list_master[index] = fix
            continue
        elif re.match("^([0-9A-Fa-f]{12})$", item):
            # only 12 characters provided, add in the :'s
            fix = item
            fix = ":".join(fix[i:i + 2] for i in range(0, len(fix), 2))
            fix = fix.upper()
            mac_list_master[index] = fix
            continue
        else:
            # incorrect mac used
            broken_macs.append(item)
            indexes_for_deletion.append(index)  # make sure this one doesn't get used in the master list
            continue

    # make sure the indexes get removed here
    indexes_for_deletion = indexes_for_deletion[::-1]  # flip the list, this is important because we need to remove the larger indexes first
    for index in indexes_for_deletion:
        del mac_list_master[index]
    del indexes_for_deletion[:]  # make sure that the index list is reset after deletion

    if len(broken_macs) > 0:
        messagebox.showinfo("NOTIFICATION", str(len(broken_macs)) + " MAC Address(es) will be excluded when the "
                            "deletion process takes place because of incorrect formatting. If this is important, "
                            "make sure all MAC Addresses in the CSV file are correct.")


def ssh_connect_csv():
    del deleted_list[:]  # make sure previous list is gone before proceeding
    del not_deleted_list[:]  # make sure previous list is gone before proceeding
    total_deleted = 0
    result_text = ""
    total_to_delete = len(mac_list_master)

    for hostname in activeList:
        try:
            controller = netmiko.ConnectHandler(ip=hostname.rstrip(), device_type="aruba_os",
                                                username="api-login", password="Arub@08!", secret="Password1")
        except netmiko.ssh_exception.NetMikoTimeoutException:
            messagebox.showinfo("SSH Failure", "SSH connection to '" + hostname + "' timed out. You may not "
                                               "be connected to the UNH admin network, or the hostname "
                                               "provided is invalid.",
                                icon="error")
            return
        except netmiko.ssh_exception.AuthenticationException:
            messagebox.showinfo("SSH Failure", "SSH connection to '" + hostname + "' failed. "
                                                                                  "Incorrect username/password"
                                                                                  " was entered.",
                                icon="error")
            return

        except ValueError:
            messagebox.showinfo("SSH Failure", "SSH connection to '" + hostname + "' failed. An incorrect "
                                                                                  "value was used. "
                                                                                  "Make sure 'device_type' "
                                                                                  "and 'secret' are correct.",
                                icon="error")
            return

        result_text += "Controller: " + hostname + "\n"
        for mac in mac_list_master:
            output = controller.send_command("aaa user delete mac " + mac)
            if output[0] == "1":
                total_deleted += 1
                total_to_delete -= 1
                deleted_list.append(mac)
                result_text = result_text + mac + ",Deleted" + "\n"
            elif output[0] == "0":
                not_deleted_list.append(mac)
                result_text = result_text + mac + ",Not deleted" + "\n"
        result_text += "\n"

        controller.disconnect()

    messagebox.showinfo("Finished", str(total_deleted) + " MAC Address(es) were deleted\n\n" +
                        str(total_to_delete) + " MAC Address(es) were not deleted")

    result = messagebox.askquestion("Save Results", 'Would you like to save the results?\n'
                                                    'By choosing "Yes" you will be prompted to choose '
                                                    'a name and location of the results file.'
                                    , icon='warning')
    if result == 'yes':
        try:
            save_csv_results(result_text)
        except PermissionError:
            messagebox.showinfo("Could Not Save", "Could not save the file because there was a permission error. "
                                                  "The file may already be open on your computer. If this is the "
                                                  "issue, try closing the file and running the deletion again."
                                , icon='error')


def save_csv_results(result):
    save_file = filedialog.asksaveasfile(mode='w', defaultextension=".csv", title='Save Results',
                                         filetypes=(("csv file", "*.csv"), ("all files", "*.*")))
    if save_file is None:  # if "cancel" is clicked
        return

    save_file.write(result)

    save_file.close()


def hostname_add():
    hostname_to_add = ""
    if hostnameEntry.get():
        hostname_to_add = hostnameEntry.get()

    if (hostname_to_add != "") and (hostname_to_add in activeList):
        messagebox.showinfo("Add Hostname", "The hostname you are trying to add is already in the active hostname list")
    elif hostname_to_add != "":
        result = messagebox.askquestion("Add Hostname",
                                        'Are you sure you would like to add the hostname '
                                        '"' + hostname_to_add + '" to the active hostname list?'
                                        , icon='warning')
        if result == 'yes':
            activeList.append(hostname_to_add)
            new_active = ""
            for hostname in activeList:
                new_active = new_active + hostname + "\n"
            active.set(new_active)
            activeHostnamesListLabel.config(text=active.get())

            # WRITE TO HOSTNAME FILE HERE
            hostname_write = open("hostnames.txt", "w")
            hostname_write.write(new_active)
            hostname_write.close()


def hostname_remove():
    hostname_to_remove = ""
    if hostnameEntry.get():
        hostname_to_remove = hostnameEntry.get()

    if (hostname_to_remove != "") and (hostname_to_remove not in activeList):
        messagebox.showinfo("Remove Hostname", "The hostname you are trying to remove is not in the "
                                               "active hostname list")
    elif hostname_to_remove != "":
        result = messagebox.askquestion("Remove Hostname",
                                        'Are you sure you would like to remove the hostname '
                                        '"' + hostname_to_remove + '" from the active hostname list?'
                                        , icon='warning')
        if result == 'yes':
            activeList.remove(hostname_to_remove)
            new_active = ""
            for hostname in activeList:
                new_active = new_active + hostname + "\n"
            active.set(new_active)
            activeHostnamesListLabel.config(text=active.get())

            # WRITE TO HOSTNAME FILE HERE
            hostname_write = open("hostnames.txt", "w")
            hostname_write.write(new_active)
            hostname_write.close()


mainWindow = tkinter.Tk()
mainWindow.geometry("600x400")  # width x height
mainWindow.title("Delete Client from Controller")
background_color = "#ECECEC"
mainWindow.resizable(False, False)  # make it not resizeable

# ADD TAB CONTROL
tabControl = ttk.Notebook(mainWindow)
tabControl.pack(expand=1, fill="both")  # match window size

# MAKE TABS
tab1 = ttk.Frame(tabControl)
tabControl.add(tab1, text="Delete")

tab2 = ttk.Frame(tabControl)
tabControl.add(tab2, text="Advanced")

tab3 = ttk.Frame(tabControl)
tabControl.add(tab3, text="Settings")

# TAB 1 - DELETE ######################################################################################################

# ENTER THE USERNAME/MAC/IP AREA
enterLabel = tkinter.Label(tab1, text="Enter username/mac/ip for deletion: ", bg=background_color)
enterLabel.place(x=27, y=10)  # x from left, y from top

deletionVar = tkinter.StringVar(mainWindow)
deletionVar.set("")  # default value (do not change this one)
deletionEntry = tkinter.Entry(tab1, textvariable=deletionVar, width=20, highlightbackground=background_color, disabledbackground=background_color)
deletionEntry.place(x=277, y=10)

typeLabel = tkinter.Label(tab1, text="Choose type: ", bg=background_color)
typeLabel.place(x=166, y=50)

dropOption = tkinter.StringVar(mainWindow)
dropOption.set("MAC Address")  # default value (change this one if needed)
dropdown = tkinter.OptionMenu(tab1, dropOption, "MAC Address", "Username", "IP Address")  # if above is changed, change order here too
dropdown.config(width=13, bg=background_color)
dropdown.place(x=277, y=50)

# SELECT ITEM
selectButton = tkinter.Button(tab1, text="SELECT", width=20, highlightbackground=background_color, command=select)
selectButton.place(x=30, y=100)

# SELECTED AREA
selectedVarLabel = tkinter.Label(tab1, text="Selected to delete: ", bg=background_color)
selectedVarLabel.place(x=126, y=160)
selectedVarLabel2 = tkinter.Label(tab1, text="NONE SELECTED", anchor="w", fg="white", width=17, bg="red")
selectedVarLabel2.place(x=277, y=160)

selectedTypeLabel = tkinter.Label(tab1, text="Selected type: ", bg=background_color)
selectedTypeLabel.place(x=152, y=190)
selectedTypeLabel2 = tkinter.Label(tab1, text=dropOption.get(), anchor="w", fg="white", width=17, bg="red")
selectedTypeLabel2.place(x=277, y=190)

# DELETE ITEM
deleteButton = tkinter.Button(tab1, text="DELETE", width=20, highlightbackground=background_color, command=delete)
deleteButton.place(x=30, y=240)
responses = []

# TAB 2 - ADVANCED ####################################################################################################

# CHOOSE FILE BUTTON
fileButton = tkinter.Button(tab2, text="Choose MAC Address CSV File", width=25, highlightbackground=background_color, command=ask_for_file)
fileButton.place(x=30, y=20)

# CSV ENTRY
csvVar = tkinter.StringVar(mainWindow)
csvVar.set("")  # default value (do not change this one)
csvEntry = tkinter.Entry(tab2, textvariable=csvVar, width=50, highlightbackground=background_color, disabledbackground=background_color)
csvEntry.place(x=30, y=60)

# SELECT CSV
mac_list_master = []
csv_selectButton = tkinter.Button(tab2, text="SELECT THIS FILE", width=20, highlightbackground=background_color, command=fill_mac_list)
csv_selectButton.place(x=30, y=110)

# SELECTED CSV AREA
csv_full_deletionVar = tkinter.StringVar(mainWindow)
csv_full_deletionVar.set("NONE SELECTED")  # default value (do not change this one)
selectedCSVLabel = tkinter.Label(tab2, text="Selected: ", bg=background_color)
selectedCSVLabel.place(x=30, y=150)
selectedCSVLabel2 = tkinter.Label(tab2, text="NONE SELECTED", anchor="w", fg="white", width=17, bg="red")
selectedCSVLabel2.place(x=110, y=150)
broken_macs = []

# DELETE ITEM CSV
csv_deleteButton = tkinter.Button(tab2, text="DELETE ALL MAC ENTRIES", width=25, highlightbackground=background_color, command=delete_csv)
csv_deleteButton.place(x=30, y=195)
deleted_list = []
not_deleted_list = []

# TAB 3 - SETTINGS ####################################################################################################

# HOSTNAME LABEL
hostnameLabel = tkinter.Label(tab3)
hostnameLabel.config(text="Enter hostname to add or remove:", bg=background_color)
hostnameLabel.place(x=30, y=30)

# HOSTNAME ENTRY
hostnameVar = tkinter.StringVar(mainWindow)
hostnameVar.set("")  # default value (do not change this one)
hostnameEntry = tkinter.Entry(tab3, textvariable=hostnameVar, width=52, highlightbackground=background_color, disabledbackground=background_color)
hostnameEntry.place(x=30, y=60)

# ADD HOSTNAME
hostname_add_Button = tkinter.Button(tab3, text="ADD HOSTNAME", width=20, command=hostname_add, highlightbackground="#50FB70")
hostname_add_Button.place(x=70, y=100)

# REMOVE HOSTNAME
hostname_remove_Button = tkinter.Button(tab3, text="REMOVE HOSTNAME", width=20, command=hostname_remove, highlightbackground="#FF4D4D")
hostname_remove_Button.place(x=300, y=100)

# ACTIVE HOSTNAMES LABEL
activeHostnamesLabel = tkinter.Label(tab3)
activeHostnamesLabel.config(text="ACTIVE HOSTNAME LIST:", bg=background_color)
activeHostnamesLabel.place(x=30, y=150)

# ACTIVE HOSTNAMES LIST LABEL
activeHostnamesListLabel = tkinter.Label(tab3)
activeHostnamesListLabel.config(bg=background_color)
activeHostnamesListLabel.place(x=30, y=180)

# POPULATE LIST
active = tkinter.StringVar(mainWindow)
active.set("")
activeList = []
try:
    hostnameFile = open("hostnames.txt", "r")
    hostLines = hostnameFile.readlines()
    for line in hostLines:
        active.set(active.get() + line)
        activeList.append(line.rstrip())
    hostnameFile.close()
except FileNotFoundError:
    hostnameVar.set("The 'hostnames.txt' file must be present to add or remove.")
    hostnameEntry.config(state='disabled')
    hostname_add_Button.config(state='disabled')
    hostname_remove_Button.config(state='disabled')
    # make a label which says it wasn't found and place it in tab 3 area
    no_fileLabel = tkinter.Label(tab3)
    no_fileLabel.config(text="'hostnames.txt' could not be found.", bg=background_color)
    no_fileLabel.place(x=30, y=180)
    # make sure the user cannot input stuff from tab 1 or 2
    deletionVar.set("see Settings tab")
    deletionEntry.config(state='disabled')
    selectButton.config(state='disabled')
    deleteButton.config(state='disabled')
    fileButton.config(state='disabled')
    csvVar.set("see Settings tab")
    csvEntry.config(state='disabled')
    csv_selectButton.config(state='disabled')
    csv_deleteButton.config(state='disabled')

activeHostnamesListLabel.config(text=active.get(), justify="left")

mainWindow.mainloop()
