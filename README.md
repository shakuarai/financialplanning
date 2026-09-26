# financialplanning

A one-page marketing site for **Horizon Wealth Planning**, a demo financial planning firm.

**Live site:** https://shakuarai.github.io/financialplanning/

![Horizon Wealth Planning home page at desktop width](docs/screenshot.png)

The whole site lives in [`index.html`](index.html): the HTML, the CSS in a `<style>` tag and plain JavaScript in a `<script>` tag. It uses no frameworks, build tools or external JS or CSS libraries.

## What's on the page

- **Header:** sticky navigation. The link for the section you're viewing is highlighted, and there's a mobile menu.
- **Hero:** headline, calls to action and statistics that count up.
- **Testimonials:** a carousel showing 1, 2 or 3 cards depending on screen width, with dot navigation.
- **Contact:** an enquiry form with validation for every field, and error messages that screen readers announce.
- **Footer:** newsletter sign-up, social links and a back-to-top button.

The layout is mobile-first, with breakpoints at 768px and 1024px. Animations are turned off for anyone who has asked their system for reduced motion.

## Running it

There's nothing to install or build. Open the file in a browser:

```sh
open index.html
```

## Editing

- Colours and spacing are CSS custom properties on `:root`.
- The CSS, HTML and JS are divided by numbered comment banners, such as `/* 7. TESTIMONIALS CAROUSEL */`.
- To fade an element in as it scrolls into view, give it the `.fade-in` class. Add `.delay-1`, `.delay-2` or `.delay-3` to stagger it.

Some things must change together across the CSS, HTML and JS:

- **Carousel:** the cards per view in `perView()` must match the `.carousel__slide` `flex-basis` at each breakpoint.
- **Hero stats:** each count-up's `data-target` and its hidden screen-reader value must be edited together.
- **Enquiry form:** each field needs a validator, an `#{name}-error` element and an entry in the submitted data, all keyed by the field's `name`.

## Deployment

The site is hosted on GitHub Pages. On every push to `main`, the workflow in [`.github/workflows/pages.yml`](.github/workflows/pages.yml) publishes `index.html` only, so the rest of the repo isn't served.

## Demo limitations

This is a front-end demo and isn't ready for production:

- Neither form sends data anywhere. They only log it to the browser console, and the enquiry form fakes a 1.5-second request.
- The contact details, social links, testimonial avatars (from pravatar.cc) and hero photo (from Unsplash) are placeholders.
