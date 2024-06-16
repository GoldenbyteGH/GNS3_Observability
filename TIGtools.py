from jinja2 import Environment, FileSystemLoader


class Flex_telegraf:
    ENV = Environment(loader=FileSystemLoader('.'))

    def __init__(self, tg_conf, template_name="telegraf_snmp.j2"):
        self.tg_template = Flex_telegraf.ENV.get_template(template_name)
        self.tg_conf = tg_conf

    def confapply(self, influx_ip, influx_port, flex_ips):
        for line in self.tg_template.render(
                    influx_ip=influx_ip,
                    influx_port=influx_port,
                    flex_ips=flex_ips):
            self.tg_conf.writelines(line)


class Flex_grafana:
    ENV = Environment(loader=FileSystemLoader('.'))

    def __init__(self, rp_tmp_name='grafana_template.j2'):

        self.rp_template = Flex_grafana.ENV.get_template(rp_tmp_name)

    def build_dash(self, device_list, dashboard=open('flex_dashboard.json', 'w')):

        gridpos = [8, 12, 0, 1]
        panel_size = (12, 8)
        grids_xy = []

        for count, device in enumerate(device_list):
            for interface in device.interfaces:
                grids_xy.append((
                    gridpos[2], gridpos[3] + (panel_size[1]*(count-1 if count > 0 else count)),
                    gridpos[1], gridpos[3] + (panel_size[1]*(count-1 if count > 0 else count))))

        for line in self.rp_template.render(device_list=device_list,
                                            grids_xy=grids_xy,
                                            panel_size=panel_size):
            dashboard.writelines(line)



# Discover telnet ports
# class SNMP_Telegraf:
#    def __init__(self, conf):
#        self.conf = conf
#
#    def telnet_scan(self, start_port=5000, end_port=6000):
#
#        # common used range = 5000-6000
#        try:
#
#            for port in range(start_port, end_port):
#                socket.setdefaulttimeout(1)
#                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#                try:
#                    result = s.connect((self.gnsvm, port))
#                except ConnectionError:
#                    continue
#
#                if result is None:
#                    try:
#                        telnetlib.Telnet(self.gnsvm, port)
#                        self.telnet_ports.append(port)
#                    except ConnectionError:
#                        pass
#                s.close()
#        except KeyboardInterrupt:
#            print("\n Exiting Program !!!!")
#            sys.exit()



