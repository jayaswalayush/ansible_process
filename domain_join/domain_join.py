import subprocess

import yaml


class DomainJoin:
    def __init__(self):
        self.ip_address = "${p:ip_address}"
        self.operating_system = "${p:operating_system}"
        self.ansible_user = "${p:ansible_user}"
        self.ansible_password = "${p:ansible_password}"
        self.work_dir = "${p:working.dir}"

    def process_request(self):
        ip_address_list = self.ip_address.strip().split(",")
        print("IP Address : " + str(ip_address_list))
        result = self.domain_join(ip_address_list)
        if not result:
            command = "rm -rf {}".format(self.work_dir)
            subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            raise Exception(
                "Sorry, Failed in joining the domain on all VMs. Please rectify the errors above and try again.")

    def domain_join(self, ip_address_list):
        result = False
        if self.generate_inventory(ip_address_list):
            try:
                command = "cd {}; ansible-playbook -vvv -i inventory.yml playbook.yml".format(self.work_dir)
                process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                if process.returncode == 0:
                    result = True
                    print("Domain Join Success with Output : " + str(process.stdout.decode()))
                else:
                    print("Domain Join Failed with Output : " + str(process.stdout.decode()))
            except Exception as error:
                print("Domain Join Failed with Output : " + str(error))
        return result

    def generate_inventory(self, ip_address_list):
        result = False
        if len(ip_address_list) > 0:
            inventory_dict = dict()
            os_dict = dict()
            hosts_dict = dict()
            vars_dict = dict()
            vars_dict['ansible_user'] = self.ansible_user
            if self.operating_system == "windows":
                vars_dict['ansible_password'] = self.ansible_password
                vars_dict['ansible_connection'] = 'winrm'
                vars_dict['ansible_port'] = 5986
                vars_dict['ansible_winrm_server_cert_validation'] = 'ignore'
                vars_dict['ansible_python_interpreter'] = 'auto'
            else:
                vars_dict['ansible_ssh_pass'] = self.ansible_password
                vars_dict['ansible_become_pass'] = self.ansible_password
                vars_dict['ansible_connection'] = 'ssh'
            for ip_address in ip_address_list:
                host_dict = dict()
                host_dict['ansible_host'] = ip_address
                hosts_dict[ip_address] = host_dict
            os_dict['hosts'] = hosts_dict
            os_dict['vars'] = vars_dict
            inventory_dict[self.operating_system] = os_dict
            print("Inventory File : " + str(inventory_dict))
            with open('inventory.yml', 'w') as yaml_file:
                yaml.dump(inventory_dict, yaml_file, default_flow_style=False)
                print("Successfully created Inventory File")
                result = True
        return result


domain_join = DomainJoin()
domain_join.process_request()
