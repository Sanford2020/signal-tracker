# H3-03 Staging User Access Token

H3-01 ensured production workspace access requires membership, but the identity signal was still `X-User-Email`, which can be spoofed.

This change adds a staging-grade user token. It is not a full auth system, but it prevents basic email-header spoofing in hosted staging.
