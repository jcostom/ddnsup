# ddnsup - Dynamic DNS Updater

For quite some time, I've been maintaining 2 different Dynamic DNS updaters - one for Cloudflare, another for DNS Made Easy. This is the merger of those two projects.

Example docker-compose files for each Cloudflare and DNS Made Easy are in the GitHub repo.

If you're not using docker-compose, and prefer to just simply run Docker from the CLI, here's an example to invoke the container for Cloudflare:

```bash
docker run -d \
    --name=ddnsup \
    --user 1000:1000 \
    --restart=unless-stopped \
    -v /var/docks/ddnsup:/config \
    -e PROVIDER=cf \
    -e APITOKEN=24681357-abc3-12345-a1234-987654321 \
    -e CFZONEID=123456 \
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
    -e APIKEY=24681357-abc3-12345-a1234-987654321 \
    -e SECRETKEY=123456-ab123-123ab-9876-123456789 \
    -e DMEZONEID=123456 \
    -e RECORDS=host1,host2 \
    -e USETELEGRAM=1 \
    -e CHATID=0 \
    -e MYTOKEN=1111:1111-aaaa_bbbb.cccc \
    -e SITENAME='HOME' \
    -e TZ='America/New_York' \
    ghcr.io/jcostom/ddnsup
```
