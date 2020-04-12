#!/usr/bin/python3

import os
import argparse
import random
import docker
import typing
import ipaddress
from dataclasses import dataclass
from graphviz import Graph
from graphviz.backend import FORMATS
from datetime import datetime

# colorlover.scales["12"]["qual"]["Paired"] converted to hex strings

nets_blacklist = os.environ["NETS_BLACKLIST"].split(",")
containers_blacklist = os.environ["CONTAINERS_BLACKLIST"].split(",")

nets_blacklist_dict = { nets_blacklist[i]: i for i in range(0, len(nets_blacklist)) }
containers_blacklist_dict = { containers_blacklist[i]: i for i in range(0, len(containers_blacklist)) }

DISTINCT_COLORMAP = {
    "dimgray": "#696969",
    "saddlebrown": "#8b4513",
    "darkgreen": "#006400",
    "darkmagenta": "#8b008b",
    "red": "#ff0000",
    "darkorange": "#ff8c00",
    "yellow": "#ffff00",
    "chartreuse": "#7fff00",
    "royalblue": "#4169e1",
    "aqua": "#00ffff",
    "deepskyblue": "#00bfff",
    "blue": "#0000ff",
    "fuchsia": "#ff00ff",
    "plum": "#dda0dd",
    "lightgreen": "#90ee90",
    "deeppink": "#ff1493",
    "navajowhite": "#ffdead"
}

FONT_SIZE="10"
EDGE_WIDTH = "2"
EDGE_MIN_LEN = "8"

BG_COLOR = DISTINCT_COLORMAP["dimgray"]
CONTAINER_COLOR = DISTINCT_COLORMAP["navajowhite"]
NOTE_COLOR = DISTINCT_COLORMAP["lightgreen"]
COLORS = [
    DISTINCT_COLORMAP["saddlebrown"], 
    DISTINCT_COLORMAP["darkgreen"], 
    DISTINCT_COLORMAP["darkmagenta"], 
    DISTINCT_COLORMAP["red"], 
    DISTINCT_COLORMAP["darkorange"], 
    DISTINCT_COLORMAP["yellow"], 
    DISTINCT_COLORMAP["chartreuse"], 
    DISTINCT_COLORMAP["aqua"], 
    DISTINCT_COLORMAP["deepskyblue"], 
    DISTINCT_COLORMAP["blue"], 
    DISTINCT_COLORMAP["plum"], 
    DISTINCT_COLORMAP["lightgreen"], 
    DISTINCT_COLORMAP["deeppink"], 
    DISTINCT_COLORMAP["fuchsia"], 
    DISTINCT_COLORMAP["royalblue"], 
    DISTINCT_COLORMAP["navajowhite"]
]
i = 0


@dataclass
class Network:
    name: str
    gateway: str
    internal: bool
    isolated: bool
    color: str


@dataclass
class Interface:
    endpoint_id: str
    address: str


@dataclass
class Container:
    container_id: str
    name: str
    interfaces: typing.List[Interface]


@dataclass
class Link:
    container_id: str
    endpoint_id: str
    network_name: str


def get_unique_color() -> str:
    global i

    if i < len(COLORS):
        c = COLORS[i]
        i += 1
    else:
        # Generate random color if we've already used the 12 preset ones
        c = "#%06x".format(random.randint(0, 0xFFFFFF))

    return c


def get_networks(client: docker.DockerClient, verbose: bool) -> typing.Dict[str, Network]:
    networks: typing.Dict[str, Network] = {}

    for net in sorted(client.networks.list(), key=lambda k: k.name):
        try:
            gateway = net.attrs["IPAM"]["Config"][0]["Gateway"]
        except (KeyError, IndexError):
            try:
                subnet = net.attrs["IPAM"]["Config"][0]["Subnet"]
                hosts = list(ipaddress.IPv4Network(subnet).hosts())
                first_host = hosts[0]
                gateway = first_host.exploded
            except (KeyError, IndexError):
                # This network doesn't seem to be used, skip it
                continue
        
        if net.name in nets_blacklist_dict:
            # This network has been blacklisted
            continue

        internal = False
        try:
            if net.attrs["Internal"]:
                internal = True
        except KeyError:
            pass

        isolated = False
        try:
            if net.attrs["Options"]["com.docker.network.bridge.enable_icc"] == "false":
                isolated = True
        except KeyError:
            pass

        if verbose:
            print(f"Network: {net.name} {'internal' if internal else ''} {'isolated' if isolated else ''} gw:{gateway}")

        color = get_unique_color()
        networks[net.name] = Network(net.name, gateway, internal, isolated, color)

    return networks


def get_containers(client: docker.DockerClient, verbose: bool) -> (typing.List[Container], typing.List[Link]):
    containers: typing.List[Container] = []
    links: typing.List[Link] = []

    for container in client.containers.list():
        
        if container.name in containers_blacklist_dict:
            # This container has been blacklisted
            continue

        interfaces: typing.List[Interface] = []

        # Iterate over container interfaces
        for net_name, net_info in container.attrs["NetworkSettings"]["Networks"].items():
            endpoint_id = net_info["EndpointID"]

            interfaces.append(Interface(endpoint_id, net_info['IPAddress']))
            links.append(Link(container.id, endpoint_id, net_name))

        if verbose:
            print(f"Container: {container.name} {''.join([iface.address for iface in interfaces])}")

        containers.append(Container(container.id, container.name, interfaces))

    return containers, links


def draw_network(g: Graph, net: Network):
    label = f"{{<gw_iface> {net.gateway} | {net.name}"
    if net.internal:
        label += " | Internal"
    if net.isolated:
        label += " | Containers isolated"
    label += "}"

    g.node(f"network_{net.name}",
           shape="Mrecord",
           label=label,
           fontsize=FONT_SIZE,
           margin="0.20,0.05",
           fillcolor=net.color,
           style="filled"
           )


def draw_container(g: Graph, c: Container):
    iface_labels = [f"<{iface.endpoint_id}> {iface.address}" for iface in c.interfaces]

    label = f"{{ {c.name} | {{ {'|'.join(iface_labels)} }} }}"

    g.node(f"container_{c.container_id}",
           shape="record",
           label=label,
           fontsize=FONT_SIZE,
           margin="0.20,0.05",
           fillcolor=CONTAINER_COLOR,
           style="filled"
           )


def draw_link(g: Graph, networks: typing.Dict[str, Network], link: Link):
    g.edge(f"container_{link.container_id}:{link.endpoint_id}",
           f"network_{link.network_name}",
           penwidth=EDGE_WIDTH,
           minlen=EDGE_MIN_LEN,
           color=networks[link.network_name].color
           )


def generate_graph(verbose: bool, file: str):
    docker_client = docker.from_env()

    networks = get_networks(docker_client, verbose)
    containers, links = get_containers(docker_client, verbose)

    if file:
        base, ext = os.path.splitext(file)
        g = Graph(comment="Docker Network Graph", engine="sfdp", format=ext[1:], graph_attr=dict(splines="true",bgcolor=BG_COLOR,rankdir="LR"))
    else:
        g = Graph(comment="Docker Network Graph", engine="sfdp", graph_attr=dict(splines="true",bgcolor=BG_COLOR,rankdir="LR"))

    g.node(f"infobox",
           shape="note",
           label=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
           fontsize=FONT_SIZE,
           margin="0.20,0.05",
           fillcolor=NOTE_COLOR,
           style="filled"
           )

    for _, network in networks.items():
        draw_network(g, network)

    for container in containers:
        draw_container(g, container)

    for link in links:
        draw_link(g, networks, link)

    if file:
        g.render(base)
    else:
        print(g.source)


def graphviz_output_file(filename: str):
    ext = os.path.splitext(filename)[1][1:]
    if ext.lower() not in FORMATS:
        raise argparse.ArgumentTypeError("Must be valid graphviz output format")
    return filename


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Visualize docker networks.")
    parser.add_argument("-v", "--verbose", help="Verbose output", action="store_true")
    parser.add_argument("-o", "--out", help="Write output to file", type=graphviz_output_file)
    args = parser.parse_args()

    generate_graph(args.verbose, args.out)
