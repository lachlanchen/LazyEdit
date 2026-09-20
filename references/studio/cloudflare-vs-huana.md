# Transport choice, 2026-09-20

Selected: existing HuanaYun host for an isolated LazyEdge gateway. Its recorded
1 GiB RAM and 2 Mbps connection suit forwarding, not models, video conversion,
or publication browsers. 100 MB through a saturated 2 Mbps link takes at least
about 6 minutes 40 seconds, plus overhead. Chunking improves recovery, not raw
bandwidth. Concurrent uploads share that bandwidth with other server traffic.

Cloudflare Quick Tunnels are suitable for temporary tests: random hostname,
no SLA/uptime guarantee, 200 concurrent request limit and no SSE. They cannot
serve as the stable account-link issuer for this deployment.
[Official Quick Tunnels documentation](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/do-more-with-tunnels/trycloudflare/).

A named Cloudflare Tunnel is a future option for the same origin, but needs a
managed zone/account and a reviewed route. Free/Pro request uploads are limited
to 100 MB, Business 200 MB and Enterprise 500 MB by default; chunks are still
necessary. [Cloudflare upload limits](https://developers.cloudflare.com/network/maximum-upload-size/).
Cloudflare's rules for video/large-file delivery and paid product usage must
also be reviewed before moving this media service behind the CDN.
[Routing documentation](https://developers.cloudflare.com/tunnel/concepts/routing/).

No Cloudflare subscription, paid plan, DNS nameserver migration or account
purchase was performed. The existing HuanaYun plan incurs its existing hosting
and bandwidth costs; this work did not change the plan or provision another VM.
