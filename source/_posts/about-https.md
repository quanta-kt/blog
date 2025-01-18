---
title: About the "S" in "HTTPS"
date: 2025-01-18
tags:
  - Computing
  - Networking
---

_Of course, this is not about the 19th letter of the Alphabet_

## Prelude

This article is mostly my attempt of educating internet users with little to no
technical background about security and privacy on the internet. I have therefore
made an attempt to avoid technical jargon. This might also be little too
oversimplified. If you program for the web or if you are a techie and are seeking
technical answers, this article might not satisfy your curiosity.

## A network of networks

You have probably heard the phrase that internet is "network of networks" or "system
of interconnected networks". This article focuses on consequences of that fact on
your security and privacy rather than making an attempt to most accurately teach you
what that phrase _means_. I think it still worth shedding some light on it though:

- Internet is a network composed of networks: your home network is connected to your
  ISP's which is likely connected to other huge networks owned by other ISPs,
  governments, institutions, etc.

- Any information you communicate over any network (not just public internet) is
  broken down into small chunks which networking nerds call "packets".

- The interconnected networks co-operate with each other to forward packets from one
  network to next so that every device on the internet is able to communicate with the
  other.

## Packet forwarding

Devices in the same network are "directly connected" and can exchange packets easily
(Psst, this is how local file sharing technologies such as Apple's AirDrop work).

However, things get tricky when you try sending something to a device external to
your home network through public internet. Not every device on the internet shares
a _direct_ connection. However, they are still able to communicate through [_Packet
forwarding_](https://en.wikipedia.org/wiki/Packet_forwarding).

Every network has a "default gateway" or, in simpler terms, a _router_. When a device
determines that the device it is trying to send a packet to is not on the same
network, it instead forwards it to the default gateway of the network. The default
gateway is then responsible for forwarding the packet to one of the external networks
it is connected to. For most home routers, there is exactly one "external network"
which is the one owned by your ISP. Once the packet arrives to the ISP, it forwards
it to some other network which is likely to be able to ultimately forward it to the
intended destination. The packet therefore hops through multiple networks before
eventually arriving to the destination.

Some of you should already see where this is going.

### Determining path to a host

There is a neat tool that allows us to see what path IP packets will take in order
to reach the destination host:
[traceroute](https://www.man7.org/linux/man-pages/man8/traceroute.8.html).

Lets see what path my machine takes to reach exmaple.com:

```bash
$ traceroute example.com
traceroute to example.com (96.7.128.198), 64 hops max, 40 byte packets
 1  dlinkrouter (192.168.0.1)  4.555 ms  3.629 ms  3.092 ms
 2  192.168.1.1 (192.168.1.1)  4.310 ms  4.062 ms  3.784 ms
 3  * * *
 4  dhcp-192-217-37.in2cable.com (203.192.217.37)  12.343 ms  12.761 ms  12.677 ms
 5  115.117.107.141.static-kolkatta.vsnl.net.in (115.117.107.141)  12.914 ms  12.643 ms  12.784 ms
 6  172.31.244.45 (172.31.244.45)  33.850 ms  34.377 ms  40.122 ms
 7  ix-ae-4-2.tcore2.cxr-chennai.as6453.net (180.87.37.1)  29.922 ms  29.828 ms  29.742 ms
 8  if-ae-3-3.tcore1.cxr-chennai.as6453.net (180.87.36.5)  267.149 ms  268.349 ms  267.468 ms
 9  if-bundle-26-2.qcore1.cxr-chennai.as6453.net (180.87.36.139)  337.977 ms  251.444 ms  252.929 ms
10  if-ae-13-2.tcore1.svw-singapore.as6453.net (180.87.36.83)  253.585 ms  250.924 ms  248.135 ms
11  if-et-23-2.hcore2.kv8-chiba.as6453.net (180.87.67.33)  159.542 ms  150.110 ms  142.057 ms
12  * * if-ae-20-2.tcore2.lvw-losangeles.as6453.net (64.86.252.216)  247.013 ms
13  if-ae-6-20.tcore1.eql-losangeles.as6453.net (64.86.252.66)  246.493 ms *  247.623 ms
14  if-ae-6-20.tcore1.eql-losangeles.as6453.net (64.86.252.66)  253.110 ms  259.297 ms  265.754 ms
15  a96-7-128-198.deploy.static.akamaitechnologies.com (96.7.128.198)  250.428 ms  245.797 ms  264.369 ms
```

That's a lot of hops! Did you notice the "\* \* \*" instead of hostname/IP address on
the 3rd hop? Some hosts block tracerouting, which is why traceroute is not able to
report those to us. The third hop is likely my ISP.

## The problem

By now, it should be clear that everything you do on the internet hops through
several (enterprise grade) routers accross the globe.

With this in mind, we can see how your internet activity is going through devices
owned by someone else. By nature of how internet works, these entities, especially
your ISP can see every single bit of information you send or receive over the
internet. Since these packets go through them, it is also possible for them to tamper
or filter them before sending them out to the intended recipient.

Sure, you might choose to simply trust your ISP, but keep in mind they are not the
only one involved here. Are you sure you want to let the guys mentioned below see
what you are doing online?

- Your government.
- Other governments.
- Private, for-profit organizations.
- Many others.

## Private commmunication over the public internet

At first, it might sound impossible to securely send message over the internet, after
all, our messages packets go through several thrid parties before reaching the
intended recipient. _Spoiler: it isn't._

Mathematicians and Computer Scientists have developed elaborate techniques of "hiding"
information in a way that only the person a message is intended for is able to
decipher it. In fact, techniques used to achieve this have been a subject of interest
much before internet or computers existed. Study of such methods of hiding
information is called [**Cryptography**.](https://en.wikipedia.org/wiki/Cryptography)

This article will not go into the maths involved in any real-world cryptographic
algorithms. Understanding all that maths is not as important for the purposes of
this article and I would probably not do a good job explaining them.

However, there is one classic (and simple) encryption technique (if it even qualifies
as one) that might serve as a good starting point of grasping the basic idea:

### Caesar Cipher

Imagine you must tell your friend a super secret message with a precondition that
you can not communicate directly in any way and must relay messages through a common
friend. Now say, you don't want this friend to find out what message he is relaying
for you while he does it.

Sounds tricky?

One way you could achive this is using
[**Caesar Cipher**](https://en.wikipedia.org/wiki/Caesar_cipher): you and the friend
you want to exchange messages with agree on a certain number _K_. Before relaying a
message, you substitue each letter of the message by the letter that comes _K_ letters
after the original letter in the Alphabet. For example, when K is 3, A is substitued
with D, B is substitued with E and so on. So a sentence such as "I LOVE CATS" becomes
"L ORYH FDWV" -- completely gibberish.

You apply this to transformation to all your messages before asking your common
friend to relay them. The friend realying your messages does not know K and therefore
cannot obtain the original message, only the intended recipient that knows what K is
equal to can do so.

Caesar Chipher is of course very simple and is easily broken as guessing one or more
words gives away the shared secret _K_. Modern encryption algorithms make use of much
more sophisticated techniques to hide data (that is, "encrypt") from possible
interceptors.

Before sending out packets over an untrusted network such as the internet, the
contents of packet are encrypted. Turning it back into the original data requires a
secret number which is known only to the sender and recipient of the packet. This
way, the sender is confidently able to send packets over the public internet without
ever worrying about interception of those packets by anyone other than the intended
recipient(s).

## Always use HTTPS, please

HTTPS is a secure extension of the HTTP protocol that adds the security features we
just discussed and allows secure transmission of information on the public internet.

The thing about HTTPS is though that it is an optional tech.

It is possible (but not recommended) for you to access a website over HTTP (which
does not use any encryption). In fact, while most important ones work on (some even
mandate) HTTPS, a lot of websites on the internet today only support HTTP. It is
important to stay aware of the fact that the traffic you exchange with a website over
HTTP is not encrypted and entities such as your ISP and others _could_ intercept it
if they ever want to. If you have to ask, this includes any passwords you enter on
the website any pictures you download or upload, or to put short, anything you
exchange with the website in question.

Most modern web browsers will warn you in some way if you are accessing a webpage
over HTTP. Google Chrome shows a green padlock icon beside the address bar when the
connection is secure, that is, you are viewing the webpage over HTTPS (There is
actually lots of other criteria for the padlock to be shown, but for purposes of this
article, this is all we care about).

It is also possible to configure
[Firefox](https://support.mozilla.org/en-US/kb/https-only-prefs) and
[Google Chrome](https://support.google.com/chrome/answer/10468685?hl=en&co=GENIE.Platform%3DDesktop#zippy=%2Cturn-on-always-use-secure-connections)
to only allow HTTPS traffic. Other browsers might provide simmilar configuration,
a simple web search should guide you how to do that with any popular browser of your
choice. I recommended turning it on to ensure you don't browse web over HTTP, without
having to manually verify everytime.

## Closing thoughts

Regardless of whether or not you have "something to hide", ensuring nobody is
intercepting your internet traffic should be very important. We use internet to do
all sorts of things after all -- from hobbies and entertainment to banking. Practice
your right to privacy and use HTTPS.

Also, be aware that HTTPS/SSL does not protect you from other undesired things such
as [phishing](https://en.wikipedia.org/wiki/Phishing) and other scams and frauds.

P.S. I am new to blogging; this is the first honest-to-god blog I have ever authored.
I hope you enjoyed reading it nevertheless. Do let me know what you think about it or
if I messed up somewhere :)
