---
title: I finally understand why people self-host their media
url: https://www.xda-developers.com/understand-why-people-self-host-media/
final_url: https://www.xda-developers.com/understand-why-people-self-host-media/
source_type: web
providers: brave
topic: Self-hosting in practice and the motivation for it: Docker/local-model deployment, embedding choices, privacy and data-ownership arguments, plus practitioner discourse (why Garry Tan built his own) and the own-vs-rent-your-memory debate including vendor business models.
fetched_at: 2026-08-28T20:57:47+00:00
published: 2026-01-16
content_digest: f292c56cf6e85255
---

Menu

Sign in now

Close

News

PC HardwareSubmenu
CPU

GPU

Storage

Monitors

Keyboards & Mice

SoftwareSubmenu
AI tools

Productivity

Self-Hosting

Home Lab

Other Software

Operating SystemsSubmenu
Windows

Linux

macOS

DevicesSubmenu
Single-Board Computers

Laptops

Gaming Handheld

Prebuilt PC

HomeSubmenu
Networking

Smart Home

EntertainmentSubmenu
Entertainment

Gaming

Sign in

Newsletter

Menu

Like

Follow

Followed

6

6

More Action

Summary
Generate a summary of this story

Sign in now

Claude

ESP32

AI Tools

Entertainment

Forums

Close

# I finally understand why people self-host their media

By Chandraveer Mathur

Published Jan 15, 2026, 9:00 PM EST

A seasoned mechanical design engineer turned tech reporter and reviewer, Chandraveer brings more than four years of consumer tech journalism experience to the table, with bylines at Android Police and iPhoneHacks. He's written about everything from UI and UX changes across various apps to emerging software and AI trends. At XDA, he showcases his versatility in the tech reporting space with articles rooted in personal experiences and frustrations.

Chandraveer's passion for consumer tech spills over into hobbies such as mechanical keyboards, photography, and 3D printing. With an academic background in design and manufacturing, his insatiable curiosity spans beyond the digital domain. Chandraveer's downtime is an eclectic mix of reading fiction, practicing calligraphy, conceptualizing new products, and enjoying an expansive FLAC audio library.

Sign in to your XDA account

Add Us

Addon Google

Preferred SourceGoogle News

Summary
Generate a summary of this story

Like

Like

follow

Follow

followed

Followed

Thread
6

Log in

Here is a fact-based summary of the story contents:

Try something different:

Show me the facts

Explain it like I’m 5

Give me a lighthearted recap

Using a media server on your utilities bill, inside your home, seems like a lot of work until you go about setting one up. The feeling immediately turns to regret that you should've done this sooner and saved so much on cloud subscription costs. That was my experience in a nutshell, switching from cloud providers to self-hosting for media, and the price delta only gets wider with time as a NAS gets pricier upfront and streaming services we hoped would replace cable TV become the very evil they sought to destroy, riddled with ads and confusing bundle pricing.

I was contentedly living in the walled gardens of Big Tech, happily paying my monthly tithes to Spotify, Google, and the various streaming giants for the privilege of accessing content I supposedly bought. But after a few months of tinkering with a NAS, I went from looking at the FOSS and self-hosting crowd with a mixture of confusion and mild pity to sheer adoration. It works beautifully until your favorite show vanishes due to a licensing dispute, or your subscription price hikes up for the third time in a year without adding any value. Owning the bytes comprising your media is vastly superior for the invested user who values permanence and privacy. Here is why I’m convinced that self-hosting is the only way forward, provided you are willing to shoulder the responsibility that comes with the convenience.
Related

Why self-hosting matters now more than ever in the age of cloud

Break free from reliance on the cloud and build digital independence.

Posts

By Tom Li

##
True digital ownership

###
Owning bytes of data, not access rights to them

Close

The most immediate and profound benefit is the shift from renting to owning. When you rely on Spotify or Netflix, you are merely renting access to a library that changes at the whim of corporations. I’ve had songs disappear from my playlists due to rights expirations, and movies vanish from my queue mid-watch. With self-hosting, my files sit on my hard drives. They don't decay; they don't become inaccessible when I travel, and I'm the legal team deciding what is no longer profitable to host. I can also preserve vintage shows and movies that weren't originally available in my locale, without a tech company interfering and telling me I can't watch them. It effectively eliminates the concept of restrictions on what I can see and when I can see it.

This also extends to photographs, which I click a lot of. We all do, since smartphone cameras boomed in the past decade. As a result, a vast majority of users cough up a monthly payment for iCloud and Google Photos cloud backups when faced with the possibility of losing access to old memories.

Sadly, practically every major tech company admits to scanning your photos and data to train their AI models or serve ads. If you undertake hosting these images on a local server, you're solely in charge of access controls and security. This is a massive responsibility with a tremendous upside. My data doesn't leave my house unless I want it to, and third parties cannot access my media as easily. What I mean is that I decide who has access to my Plex server, and I can revoke that access instantly. As for Plex itself profiling me through usage patterns, I'd have more control than with, say, Netflix.

##
More control over metadata and the UI

###
And the math checks out, too

Close

Perhaps the most liberating part is choosing exactly how I consume my content. I’m not forced to watch unskippable trailers or deal with an interface that pushes Recommended for You garbage over what I've stored, until I seek said recommendations. For video, I can choose between the polished look of Plex, the open-source freedom of Jellyfin, or the sheer customizability of Kodi. They are the three horsemen of self-hosted video streaming, and little else comes close. For images, I can swap between Nextcloud for syncing, Imagor for high-performance viewing, or Nomacs on the desktop. I control the UI, the transcoding quality, and the buffering settings. It’s a bespoke experience that no streaming service can match.

Another advantage only se