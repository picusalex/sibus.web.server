

function secondsToString(seconds)
{
    var numdays = Math.floor(seconds / 86400);
    var numhours = Math.floor((seconds % 86400) / 3600);
    var numminutes = Math.floor(((seconds % 86400) % 3600) / 60);
    var numseconds = ((seconds % 86400) % 3600) % 60;
    numseconds = numseconds.toFixed(0)

    if (numdays == 0 && numhours == 0 && numminutes == 0) {
        return numseconds + " secs";
    }

    if (numdays == 0 && numhours == 0) {
        return numminutes + " mins";
    }

    if (numdays == 0) {
        return numhours + " heures " + numminutes + " mins";
    }

    return numdays + " jours " + numhours + "h " + numminutes + " mins";


}

function mbpsToString(bytes)
{
    var Mbytes = bytes / (1024*1024);
    var kbytes = bytes / (1024);

    if (Mbytes > 1 ) {
        return Mbytes.toFixed(1) + " MB/sec";
    }

    if (kbytes > 1 ) {
        return kbytes.toFixed(1) + " kB/sec";
    }

    return bytes.toFixed(0) + " B/sec";


}

function bytesToString(bytes)
{
    var Gbytes = bytes / (1024*1024*1024);
    var Mbytes = bytes / (1024*1024);
    var kbytes = bytes / (1024);

    if (Gbytes > 1 ) {
        return Gbytes.toFixed(1) + " GB";
    }

    if (Mbytes > 1 ) {
        return Mbytes.toFixed(1) + " MB";
    }

    if (kbytes > 1 ) {
        return kbytes.toFixed(1) + " kB";
    }

    return bytes.toFixed(0) + " B";

}

function sleep(milliseconds) {
  var start = new Date().getTime();
  for (var i = 0; i < 1e7; i++) {
    if ((new Date().getTime() - start) > milliseconds){
      break;
    }
  }
}