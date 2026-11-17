# Setup (Day 1)

All resources are in Azure region Australia East.

## Azure
- Resource group: rg-shopstream-dev
- Storage account: stshopstreamdev (ADLS Gen2), containers landing and lake
- Databricks workspace: dbw-shopstream-dev (Premium)
- Access connector: ac-shopstream-dev, role Storage Blob Data Contributor on the storage account
- Budget: A$20 a month with email alerts

## Databricks (Unity Catalog)
- Storage credential: sc_shopstream_dev
- External locations: el_shopstream_landing (landing container), el_shopstream_lake (lake container)
- Catalogs: shopstream_dev and shopstream_prod, each with schemas bronze, silver, gold
- Volumes in shopstream_dev.bronze: raw and events (external, in the landing container), checkpoints (managed)
- Compute: serverless
