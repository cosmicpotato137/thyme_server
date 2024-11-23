# Secret Santa Pairing App

This project is a Secret Santa pairing app, designed to create Secret Santa pairings where certain groups of people cannot be paired together. It was bootstrapped with [Create React App](https://github.com/facebook/create-react-app).

## Project Structure

- `App.js`: This is the main application file. It imports and uses the `GroupMaker` and `PairViewer` components.
- `GroupMaker.js`: This component allows users to define groups of people who should not be paired together.
- `PairViewer.js`: This component displays the generated pairings.
- `scripts/SantaSelector.js`: This script contains the logic for generating the Secret Santa pairings.

## Pairing Algorithm

The algorithm works by creating a single cycle that bounces from group to group, and always chosing the next group from the group with the largest size. 

This algorithm hinges on the the Triangle Indequality. If one group is larger than all the others combined, there will be at least one element of that group that must be paired with an element of that group.

## Available Scripts

In the project directory, you can run:

### `npm start`

Runs the app in the development mode. Open [http://localhost:3000](http://localhost:3000) to view it in your browser.

### `npm test`

Launches the test runner in the interactive watch mode. See the section about [running tests](https://facebook.github.io/create-react-app/docs/running-tests) for more information.

### `npm run build`

Builds the app for production to the `build` folder. It correctly bundles React in production mode and optimizes the build for the best performance.

### `npm run eject`

**Note: this is a one-way operation. Once you `eject`, you can't go back!**

If you aren't satisfied with the build tool and configuration choices, you can `eject` at any time. This command will remove the single build dependency from your project.

## Learn More

You can learn more about Create React App in the [Create React App documentation](https://facebook.github.io/create-react-app/docs/getting-started).

To learn React, check out the [React documentation](https://reactjs.org/).