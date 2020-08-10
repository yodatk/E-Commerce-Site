import React, {Component} from "react";
import {MDBContainer, MDBRow} from "mdbreact";

export class ContactUsPage extends Component {
    render() {
        return (
            <MDBContainer>
                <MDBRow style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                }}>
                    <h1>Send message to admins here, with email address for users</h1>
                </MDBRow>
            </MDBContainer>
        );
    }
}

export default ContactUsPage;