





class DeviceList {

    constructor() {
        this._devices = {};
        this.template = undefined;
    }

    parse_message(message) {

        var networks = [];
        for (var i in message.data.network) {
            var net = message.data.network[i];
            networks.push({
                address : net.address,
                interface : net.interface,
                bytes_recv : mbpsToString(net.bytes_recv),
                bytes_sent : mbpsToString(net.bytes_sent),
            })
        }

        var mounts = [];
        for (var i in message.data.filesystem) {
            var mount = message.data.filesystem[i];
            mounts.push({
                mountpoint : mount.mountpoint,
                device : mount.device,
                usage: mount.usage.toFixed(0),
                total : bytesToString(mount.total),
                free : bytesToString(mount.free),
            })
        }

        var context = {
            hostname: message.data.system.hostname,
            uptime: secondsToString(message.data.system.uptime),
            node:message.data.system.node,
            release:message.data.system.release,
            networks: networks,
            mounts: mounts,
            ram: {
                usage: message.data.ram.usage.toFixed(0)
            },
            swap: {
                usage: message.data.swap.usage.toFixed(0)
            },
            cpu: {
                usage: message.data.cpu.global.toFixed(0)
            },


        };

        var rendered = Mustache.render(this.template, context);

        return ["div-"+message.data.system.hostname, rendered];
    }
}