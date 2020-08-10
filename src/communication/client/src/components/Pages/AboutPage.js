import React, {Component} from "react";
import {MDBContainer, MDBRow} from "mdbreact";

export class AboutPage extends Component {
    render() {
        return (
            <MDBContainer>
                <MDBRow style={rowStyle}>
                    <h1>ALL PRODUCTS IN ONE PLACE</h1>
                </MDBRow>
                <MDBRow style={rowStyle}>
                    <h2>It's Amazing!</h2>
                </MDBRow>
                <MDBRow style={rowStyle}>
                    <h3>How no one thought about is sooner?</h3>
                </MDBRow>
            </MDBContainer>
        );
    }
}

const rowStyle = {
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
}

export default AboutPage;