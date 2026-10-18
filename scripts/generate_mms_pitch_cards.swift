import Foundation
import AppKit

// Load clients JSON
let currentDir = FileManager.default.currentDirectoryPath
let jsonUrl = URL(fileURLWithPath: currentDir).appendingPathComponent("data/clients.json")

guard let data = try? Data(contentsOf: jsonUrl),
      let clients = try? JSONSerialization.jsonObject(with: data) as? [[String: Any]] else {
    print("❌ Error loading clients.json")
    exit(1)
}

let assetsDir = URL(fileURLWithPath: currentDir).appendingPathComponent("assets/mms_cards")
try? FileManager.default.createDirectory(at: assetsDir, withIntermediateDirectories: true)

let width: CGFloat = 1080
let height: CGFloat = 1350

print("🎨 Generating MMS Pitch Cards for all \(clients.count) clients...")

for c in clients {
    guard let slug = c["slug"] as? String,
          let shortName = c["short_name"] as? String,
          let city = c["city"] as? String,
          let trade = c["trade"] as? String,
          let ownerName = c["owner_name"] as? String,
          let oldScore = c["competitor_pagespeed"] as? Int,
          let oldLcp = c["competitor_lcp"] as? String else {
        continue
    }

    let rep = NSBitmapImageRep(
        bitmapDataPlanes: nil,
        pixelsWide: Int(width),
        pixelsHigh: Int(height),
        bitsPerSample: 8,
        samplesPerPixel: 4,
        hasAlpha: true,
        isPlanar: false,
        colorSpaceName: .deviceRGB,
        bytesPerRow: 0,
        bitsPerPixel: 0
    )!

    NSGraphicsContext.saveGraphicsState()
    let ctx = NSGraphicsContext(bitmapImageRep: rep)!
    NSGraphicsContext.current = ctx

    // 1. Dark Modern Background Gradient
    let bgGradient = NSGradient(
        starting: NSColor(red: 9/255, green: 13/255, blue: 22/255, alpha: 1.0),
        ending: NSColor(red: 17/255, green: 24/255, blue: 39/255, alpha: 1.0)
    )!
    bgGradient.draw(in: NSRect(x: 0, y: 0, width: width, height: height), angle: -45)

    // 2. Subtle Blueprint Grid
    let gridColor = NSColor(red: 255/255, green: 255/255, blue: 255/255, alpha: 0.04)
    gridColor.setStroke()
    let gridPath = NSBezierPath()
    gridPath.lineWidth = 1.0
    var x: CGFloat = 0
    while x <= width {
        gridPath.move(to: NSPoint(x: x, y: 0))
        gridPath.line(to: NSPoint(x: x, y: height))
        x += 60
    }
    var y: CGFloat = 0
    while y <= height {
        gridPath.move(to: NSPoint(x: 0, y: y))
        gridPath.line(to: NSPoint(x: width, y: y))
        y += 60
    }
    gridPath.stroke()

    // 3. Top Header Pill
    let pillRect = NSRect(x: 80, y: height - 120, width: 440, height: 48)
    let pillPath = NSBezierPath(roundedRect: pillRect, xRadius: 24, yRadius: 24)
    NSColor(red: 59/255, green: 130/255, blue: 246/255, alpha: 0.15).setFill()
    pillPath.fill()
    NSColor(red: 59/255, green: 130/255, blue: 246/255, alpha: 0.4).setStroke()
    pillPath.stroke()

    let pillAttrs: [NSAttributedString.Key: Any] = [
        .font: NSFont.boldSystemFont(ofSize: 18),
        .foregroundColor: NSColor(red: 96/255, green: 165/255, blue: 250/255, alpha: 1.0)
    ]
    ("⚡ GOOGLE SPEED AUDIT & MOCKUP" as NSString).draw(at: NSPoint(x: 105, y: height - 108), withAttributes: pillAttrs)

    // 4. Client Name & Trade Title
    let titleAttrs: [NSAttributedString.Key: Any] = [
        .font: NSFont.systemFont(ofSize: 52, weight: .black),
        .foregroundColor: NSColor.white
    ]
    (shortName as NSString).draw(at: NSPoint(x: 80, y: height - 200), withAttributes: titleAttrs)

    let subtitleAttrs: [NSAttributedString.Key: Any] = [
        .font: NSFont.systemFont(ofSize: 26, weight: .semibold),
        .foregroundColor: NSColor(red: 148/255, green: 163/255, blue: 184/255, alpha: 1.0)
    ]
    ("\(city), NC • \(trade)" as NSString).draw(at: NSPoint(x: 80, y: height - 245), withAttributes: subtitleAttrs)

    // 5. Two Big Comparison Boxes (Current vs New Mockup)
    let boxWidth: CGFloat = 430
    let boxHeight: CGFloat = 440
    let boxY: CGFloat = height - 730

    // Left Box (Current Site - Red/Amber)
    let leftRect = NSRect(x: 80, y: boxY, width: boxWidth, height: boxHeight)
    let leftPath = NSBezierPath(roundedRect: leftRect, xRadius: 16, yRadius: 16)
    NSColor(red: 239/255, green: 68/255, blue: 68/255, alpha: 0.08).setFill()
    leftPath.fill()
    NSColor(red: 239/255, green: 68/255, blue: 68/255, alpha: 0.35).setStroke()
    leftPath.lineWidth = 2.0
    leftPath.stroke()

    let tagAttrsBad: [NSAttributedString.Key: Any] = [
        .font: NSFont.boldSystemFont(ofSize: 20),
        .foregroundColor: NSColor(red: 248/255, green: 113/255, blue: 113/255, alpha: 1.0)
    ]
    ("CURRENT MOBILE WEB" as NSString).draw(at: NSPoint(x: 120, y: boxY + boxHeight - 60), withAttributes: tagAttrsBad)

    let scoreAttrsBad: [NSAttributedString.Key: Any] = [
        .font: NSFont.systemFont(ofSize: 100, weight: .black),
        .foregroundColor: NSColor(red: 248/255, green: 113/255, blue: 113/255, alpha: 1.0)
    ]
    ("\(oldScore)" as NSString).draw(at: NSPoint(x: 120, y: boxY + boxHeight - 200), withAttributes: scoreAttrsBad)

    let scoreSubBad: [NSAttributedString.Key: Any] = [
        .font: NSFont.systemFont(ofSize: 32, weight: .bold),
        .foregroundColor: NSColor(red: 148/255, green: 163/255, blue: 184/255, alpha: 0.8)
    ]
    ("/ 100" as NSString).draw(at: NSPoint(x: 270, y: boxY + boxHeight - 165), withAttributes: scoreSubBad)

    let statBad1: [NSAttributedString.Key: Any] = [
        .font: NSFont.systemFont(ofSize: 22, weight: .medium),
        .foregroundColor: NSColor.white
    ]
    ("• Mobile Load Time: \(oldLcp)" as NSString).draw(at: NSPoint(x: 120, y: boxY + 140), withAttributes: statBad1)
    ("• 65%+ Bounces Before Load" as NSString).draw(at: NSPoint(x: 120, y: boxY + 95), withAttributes: statBad1)
    ("• Sluggish Mountain Signal Loss" as NSString).draw(at: NSPoint(x: 120, y: boxY + 50), withAttributes: statBad1)

    // Right Box (Our Mockup - Emerald Green)
    let rightRect = NSRect(x: 570, y: boxY, width: boxWidth, height: boxHeight)
    let rightPath = NSBezierPath(roundedRect: rightRect, xRadius: 16, yRadius: 16)
    NSColor(red: 16/255, green: 185/255, blue: 129/255, alpha: 0.12).setFill()
    rightPath.fill()
    NSColor(red: 16/255, green: 185/255, blue: 129/255, alpha: 0.6).setStroke()
    rightPath.lineWidth = 2.0
    rightPath.stroke()

    let tagAttrsGood: [NSAttributedString.Key: Any] = [
        .font: NSFont.boldSystemFont(ofSize: 20),
        .foregroundColor: NSColor(red: 52/255, green: 211/255, blue: 153/255, alpha: 1.0)
    ]
    ("NEW RENTAL MOCKUP" as NSString).draw(at: NSPoint(x: 610, y: boxY + boxHeight - 60), withAttributes: tagAttrsGood)

    let scoreAttrsGood: [NSAttributedString.Key: Any] = [
        .font: NSFont.systemFont(ofSize: 100, weight: .black),
        .foregroundColor: NSColor(red: 16/255, green: 185/255, blue: 129/255, alpha: 1.0)
    ]
    ("100" as NSString).draw(at: NSPoint(x: 610, y: boxY + boxHeight - 200), withAttributes: scoreAttrsGood)

    ("PERFECT" as NSString).draw(at: NSPoint(x: 800, y: boxY + boxHeight - 165), withAttributes: scoreSubBad)

    let statGood1: [NSAttributedString.Key: Any] = [
        .font: NSFont.systemFont(ofSize: 22, weight: .medium),
        .foregroundColor: NSColor.white
    ]
    ("✓ Instant Load Time: 0.8s" as NSString).draw(at: NSPoint(x: 610, y: boxY + 140), withAttributes: statGood1)
    ("✓ Direct One-Click Call Button" as NSString).draw(at: NSPoint(x: 610, y: boxY + 95), withAttributes: statGood1)
    ("✓ Cloudflare Mountain Edge CDN" as NSString).draw(at: NSPoint(x: 610, y: boxY + 50), withAttributes: statGood1)

    // 6. Value Proposition Card
    let vpRect = NSRect(x: 80, y: 280, width: width - 160, height: 380)
    let vpPath = NSBezierPath(roundedRect: vpRect, xRadius: 16, yRadius: 16)
    NSColor(red: 255/255, green: 255/255, blue: 255/255, alpha: 0.04).setFill()
    vpPath.fill()
    NSColor(red: 255/255, green: 255/255, blue: 255/255, alpha: 0.1).setStroke()
    vpPath.stroke()

    let vpHeader: [NSAttributedString.Key: Any] = [
        .font: NSFont.systemFont(ofSize: 28, weight: .bold),
        .foregroundColor: NSColor.white
    ]
    ("Turnkey Website Rental: $49 / Month Flat" as NSString).draw(at: NSPoint(x: 120, y: 590), withAttributes: vpHeader)

    let vpBullet: [NSAttributedString.Key: Any] = [
        .font: NSFont.systemFont(ofSize: 22, weight: .regular),
        .foregroundColor: NSColor(red: 203/255, green: 213/255, blue: 225/255, alpha: 1.0)
    ]
    ("• Zero setup fee • No contracts • Cancel anytime" as NSString).draw(at: NSPoint(x: 120, y: 535), withAttributes: vpBullet)
    ("• You keep and own your custom domain name" as NSString).draw(at: NSPoint(x: 120, y: 485), withAttributes: vpBullet)
    ("• Fast direct text updates & seasonal price changes included" as NSString).draw(at: NSPoint(x: 120, y: 435), withAttributes: vpBullet)
    ("• Direct caller phone routing straight to your mobile" as NSString).draw(at: NSPoint(x: 120, y: 385), withAttributes: vpBullet)

    let linkAttrs: [NSAttributedString.Key: Any] = [
        .font: NSFont.systemFont(ofSize: 22, weight: .bold),
        .foregroundColor: NSColor(red: 96/255, green: 165/255, blue: 250/255, alpha: 1.0)
    ]
    ("Preview Live Mockup: https://wnc-client-sites.pages.dev/sites/\(slug)/" as NSString).draw(at: NSPoint(x: 120, y: 320), withAttributes: linkAttrs)

    // 7. Footer Direct Operator Note
    let footerAttrs: [NSAttributedString.Key: Any] = [
        .font: NSFont.systemFont(ofSize: 20, weight: .medium),
        .foregroundColor: NSColor(red: 100/255, green: 116/255, blue: 139/255, alpha: 1.0)
    ]
    ("Local WNC Operator: Brandon Passmore • Hendersonville, NC • Text/Call: (828) 775-9908" as NSString).draw(at: NSPoint(x: 100, y: 160), withAttributes: footerAttrs)

    NSGraphicsContext.restoreGraphicsState()

    guard let pngData = rep.representation(using: .png, properties: [:]) else { continue }
    let destUrl = assetsDir.appendingPathComponent("\(slug)_mms_audit.png")
    try? pngData.write(to: destUrl)
    print("  ✓ Created MMS Card: assets/mms_cards/\(slug)_mms_audit.png")
}

print("\n🎉 All 10 MMS Pitch Cards generated successfully!")
