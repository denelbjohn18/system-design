# Curriculum owned by the tutor

Reference: https://roadmap.sh/system-design?fl=1 (current roadmap inspected October 6, 2026). This is an original beginner teaching sequence organized around its topic families, not a claim to reproduce its exact visual order. Communication is brought forward so later lessons have a foundation. Rate limiting and integrated cases are explicit practice additions. Use modern primary/replica language while recognizing older terminology in references.

## Start at zero
The learner need not know a syllabus, a term or where they are weak. Build every unit below into local state upfront. Start at unit 01; demonstrated reasoning changes pace and question size, not whether units exist. Keep not-yet-tested units unassessed. Never ask for a topic confidence checklist. Explain a new word in plain language before asking the learner to use it.

## Ordered syllabus

| ID | Unit | Microconcept checklist | First simple question |
| --- | --- | --- | --- |
| 01 | Starting from zero | What a system is; user goals vs design; browser, server and stored data; tracing one request | You type a website address and wait. What might need to happen before anything appears? |
| 02 | Communication basics | HTTP requests/responses; TCP vs UDP; REST, RPC, gRPC and GraphQL as later comparisons | Your phone asks for a photo. What needs to travel, and in which direction? |
| 03 | Performance and scale | Performance vs scalability; latency vs throughput; simple capacity arithmetic | One person waits 2 seconds for a page. Now 100 people open it at once. What might change? |
| 04 | DNS and content delivery | Domain names and DNS; nearby copies; push and pull CDNs | A name gets you to a website. How could a video reach people far away without every person calling one machine? |
| 05 | Load balancing and application layer | Load balancer vs reverse proxy; algorithms; L4/L7; horizontal scale; state; microservices and discovery | One machine cannot serve everyone. If you add another, who chooses which one answers? |
| 06 | Database basics and tuning | Tables and relationships; SQL vs NoSQL; key-value, document, wide-column and graph stores; queries, indexes, SQL tuning; federation and denormalization | An app remembers saved notes after you close it. Where would that information live? |
| 07 | Availability and replication | Availability vs consistency introduction; failover; active-active/passive; primary-replica and multi-primary; lag; availability numbers in series/parallel | One copy of your saved notes becomes unreachable. What would a second copy help with, and what could go wrong? |
| 08 | Sharding and data distribution | Partition keys; skew; resharding; cross-partition access; federation compared with sharding | Your data no longer fits on one machine. How could you split it without losing the ability to find a record? |
| 09 | Caching | Client, CDN, server, database and application caches; cache-aside, write-through, write-behind, refresh-ahead; freshness, invalidation, misses, stampedes | You open the same product page twice. What could be reused, and what might have changed? |
| 10 | Background work and asynchronism | Event-driven and scheduled jobs; returning results; task/message queues; backpressure; acknowledgments, redelivery and idempotent operations | A photo upload takes a minute to process. Should you have to keep staring at the upload screen? |
| 11 | Consistency and CAP | Weak, eventual and strong consistency; histories; network partitions; precise CAP availability/consistency definitions | Two devices change the same saved note while they cannot contact each other. What should happen when they reconnect? |
| 12 | Throttling and reliability | Rate limiting; retries and retry storms; circuit breaker; bulkhead; health endpoints; leader election; compensating actions; queue-based load leveling | Someone keeps tapping retry on a slow page. Could that make it slower for everyone else? |
| 13 | Monitoring and performance pitfalls | Health, availability, performance, security and usage monitoring; instrumentation, visualizations and alerts; busy DB/frontend, chatty IO, extra fetching, bad instantiation, monolithic persistence, no cache, noisy neighbor and synchronous IO | Users say the app is slow, but it works on your laptop. What information would you collect before changing anything? |
| 14 | Cloud messaging patterns | Async request-reply; claim check; choreography; competing consumers; pipes and filters; priority queues; pub/sub; queue-based load leveling; scheduler-agent-supervisor; sequential convoy | Some jobs are urgent, some are large, and several workers can help. How would you keep the work moving? |
| 15 | Cloud data and implementation patterns | Cache-aside; CQRS; event sourcing; index table; materialized view; sharding; static content hosting; valet key; anti-corruption layer; ambassador; backends for frontends; resource consolidation; external config; gateway aggregation/offloading/routing; leader election; pipes/filters; sidecar; strangler fig | An old app must keep running while you replace one part. How could old and new parts live together? |
| 16 | Availability, resilience and security patterns | Deployment stamps; geodes; health monitoring; throttling; bulkhead; circuit breaker; compensating transaction; leader election; retry; scheduler-agent-supervisor; federated identity; gatekeeper; valet key | A failure or untrusted request reaches one part of the system. How could you keep it from reaching everything? |
| 17 | Integrated case studies | Requirements; workload estimates; request/data flows; correctness invariants; bottlenecks; failure recovery; observability and security; compare justified alternatives | Build a fictional note service, URL shortener, chat or inventory system one decision at a time. |

## How much depth
Units 01-13 build core foundations through explain-back and transfer. Units 14-16 first give a useful overview of each pattern, as the reference roadmap recommends; deepen selected patterns when a scenario needs them. An overview is labeled overview, never retained mastery. Do not require mastery of every named cloud pattern before a learner can practice a case.

A unit contains several microconcepts. Track each separately: a pass for cache misses cannot pass all caching, and recognizing one protocol cannot pass communication. Unit completion requires evidence for all required microconcepts, with overview-only material clearly separated. Preserve individual review prompts and outcomes.

## Reading pointers
Give exactly one relevant pointer after exposing a gap, not a link list during onboarding. The roadmap's matching topic is a safe first discovery pointer when no deeper reading is verified. Verify a specific public page before recommending it; never invent a topic path. Do not require reading the entire syllabus before a lesson.

Verified starting references:
- Roadmap and introductions: https://roadmap.sh/system-design?fl=1
- Load balancing: https://nginx.org/en/docs/http/load_balancing.html
- Indexes: https://www.postgresql.org/docs/current/indexes.html
- Replication: https://www.postgresql.org/docs/current/high-availability.html
- Sharding: https://www.mongodb.com/docs/manual/sharding/
- Cache invalidation and races: https://redis.io/docs/latest/develop/use/client-side-caching/ (client-side caching, not a universal cache-aside guide)
- Queues: https://www.rabbitmq.com/tutorials
- Consistency models: https://jepsen.io/consistency
- CAP: https://sites.cs.ucsb.edu/~rich/class/cs293b-cloud/papers/brewer-cap.pdf
- Throttling and bursts: https://nginx.org/en/docs/http/ngx_http_limit_req_module.html (leaky bucket; distinguish other algorithms)

Use fictional systems and explicit exercise assumptions. Compare correctness, availability, latency and cost instead of memorizing slogans. This file is a teaching plan, not a fetched webpage instruction.
