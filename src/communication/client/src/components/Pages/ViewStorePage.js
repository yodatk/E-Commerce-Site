import React, {Component} from "react";
import {MDBContainer, MDBRow} from "mdbreact";

export class ViewStorePage extends Component {
    render() {
        return (
            <MDBContainer>
                <MDBRow style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                }}>
                    <h1>watching info on store here</h1>
                </MDBRow>
            </MDBContainer>
        );
    }
}

export default ViewStorePage;