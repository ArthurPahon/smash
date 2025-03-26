/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        "smash-red": "#e60012",
        "smash-blue": "#00a3e4",
        "smash-yellow": "#ffcc00",
        "smash-green": "#39b54a",
      },
    },
  },
  plugins: [require("@tailwindcss/forms")],
};
