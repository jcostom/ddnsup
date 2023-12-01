# ddnsup - Dynamic DNS Updater

For quite some time, I've been maintaining 3 different Dynamic DNS updaters - one for Cloudflare, another for DNS Made Easy, and yet another for DNS-O-Matic. This is the merger of those three projects.

## PLEASE NOTE:

As of version 0.9, I've done a considerable amount of variable name changes to make for more consistent naming across provider types. For example, all the Cloudflare-specific vars start with CF_, DNS Made Easy starts with DME_, and DNS-O-Matic start with DOM_. Yes, the old variable names still work for now, so your compose files, shell scripts, or whatever else shouldn't break with this release. If something got missed and is broken, please file a PR and I'll get it sorted.

As of version 1.0, I've continued the variable name changes in the spirit of consistency. Variables you should consider migrating are found below. Also in v1.0, I've introduced support for [Pushover](https://pushover.net/). See below as well. In this release, I changed the Telegram-centric variables, and as before, I maintained compatibility with the pre 1.0 variables. Please see below and consider updating to the new variable names.

That said, **please** consider updating your method of instantiation (be that CLI, compose, etc.) to the new variable naming convention. At some (yet to be determined) point in the future, I think it would make sense to remove the old variable names. I'm writing this on 27 Nov 2023, but have no immediate plans to execute on this, so you can do it at your leisure.

## Setting up Pushover

1. Sign up for an account at the [Pushover](https://pushover.net/) website and install the app on your device(s). Make note of your User Key in the app. It's easy to find it in the settings.

2. Follow their [API Docs](https://pushover.net/api) to create yourself an app you intend to use.

3. Pass the variables USE_PUSHOVER (set this to 1!), PUSHOVER_APP_TOKEN, and PUSHOVER_USER_KEY into the container and magic will happen.

## Variables to consider setting

### Required Variables

| **Var** | **Required?** | **Default** | **Description** |
|---|---|---|---|
| DEBUG | No | 0 | 0 for no debug, 1 for debug |
| IPADDR_SRC | No | https://ipv4.icanhazip.com/ | how to determine current IP |
| INTERVAL | No | 300 | how often to check to see if IP changed |
| RECORDS | Yes | (NONE) | records being updated |
| PROVIDER | Yes | (NONE) | Which provider? (cf, dme, dnsomatic) |

### Cloudflare-specific

| **Var** | **Required?** | **Default** | **Description** |
|---|---|---|---|
| CF_APITOKEN | Yes | (NONE) | Your CF API Token |
| CF_ZONEID | Yes | (NONE) | The Zone ID you're updating |
| CF_TTL | No | 1 | DNS TTL Value |
| CF_PROXIED | No | false | Is this IP being proxied by CF? |

### DNS Made Easy-specific

| **Var** | **Required?** | **Default** | **Description** |
|---|---|---|---|
| DME_APIKEY | Yes | (NONE) | API Key Value |
| DME_SECRETKEY | Yes | (NONE) | Secret Key Value |
| DME_ZONEID | Yes | (NONE) | The Zone ID you're updating |
| DME_TTL | No | 1800 | DNS TTL Value |

### DNS-O-Matic-specific

| **Var** | **Required?** | **Default** | **Description** |
|---|---|---|---|
| DOM_USER | Yes | (NONE) | User ID |
| DOM_PASSWD | Yes | (NONE) | Password |
| DOM_WILDCARD | No | NOCHG | Enable Wildcard |
| DOM_MX | No | NOCHG | MX Record |
| DOM_BACKUPMX | No | NOCHG | Backup MX Record |
| RECORDS | Yes | all.dnsomatic.com | Allows for special case of all.dnsomatic.com, which updates all of your hosts |

Example docker-compose files for each service are in the GitHub repo.

If you're not using docker-compose, and prefer to just simply run Docker from the CLI, here's an example to invoke the container for Cloudflare:

```bash
docker run -d \
    --name=ddnsup \
    --user 1000:1000 \
    --restart=unless-stopped \
    -v /var/docks/ddnsup:/config \
    -e PROVIDER=cf \
    -e CF_APITOKEN=24681357-abc3-12345-a1234-987654321 \
    -e CF_ZONEID=123456 \
    -e RECORDS=host1,host2 \
    -e USETELEGRAM=1 \
    -e CHATID=0 \
    -e MYTOKEN=1111:1111-aaaa_bbbb.cccc \
    -e SITENAME='HOME' \
    -e TZ='America/New_York' \
    -e DEBUG=0 \
    ghcr.io/jcostom/ddnsup:latest
```

or for DNS Made Easy:

```bash
docker run -d \
    --name=ddnsup \
    --user 1000:1000 \
    --restart=unless-stopped \
    -v /var/docks/ddnsup:/config \
    -e PROVIDER=dme \
    -e DME_APIKEY=24681357-abc3-12345-a1234-987654321 \
    -e DME_SECRETKEY=123456-ab123-123ab-9876-123456789 \
    -e DME_ZONEID=123456 \
    -e RECORDS=host1,host2 \
    -e USETELEGRAM=1 \
    -e CHATID=0 \
    -e MYTOKEN=1111:1111-aaaa_bbbb.cccc \
    -e SITENAME='HOME' \
    -e TZ='America/New_York' \
    ghcr.io/jcostom/ddnsup:latest
```

or for DNS-O-Matic:

```bash
docker run -d \
    --name=ddnsup \
    --user 1000:1000 \
    --restart=unless-stopped \
    -v /var/docks/ddnsup:/config \
    -e PROVIDER=dnsomatic \
    -e DOM_USER=my-username \
    -e DOM_PASSWD=my-password \
    -e RECORDS=host1,host2 \
    -e USETELEGRAM=1 \
    -e CHATID=0 \
    -e MYTOKEN=1111:1111-aaaa_bbbb.cccc \
    -e SITENAME='HOME' \
    -e TZ='America/New_York' \
    ghcr.io/jcostom/ddnsup:latest
```
