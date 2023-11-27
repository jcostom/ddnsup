# ddnsup - Dynamic DNS Updater

For quite some time, I've been maintaining 3 different Dynamic DNS updaters - one for Cloudflare, another for DNS Made Easy, and yet another for DNS-O-Matic. This is the merger of those three projects.

**NOTE**: As of version 0.9, I've done a considerable amount of variable name changes to make for more consistent naming across provider types. For example, all the Cloudflare-specific vars start with CF_, DNS Made Easy starts with DME_, and DNS-O-Matic start with DOM_. Yes, the old variable names still work for now, so your compose files, shell scripts, or whatever else shouldn't break with this release. If something got missed and is broken, please file a PR and I'll get it sorted.

That said, **please** consider updating your method of instantiation (be that CLI, compose, etc.) to the new variable naming convention. At some (yet to be determined) point in the future, I think it would make sense to remove the old variable names. I'm writing this on 27 Nov 2023, but have no immediate plans to execute on this, so you can do it at your leisure.

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
