import React, {Component} from "react";
import {MDBContainer, MDBRow} from "mdbreact";

export class SingleStoreManagePage extends Component {
    render() {
        return (
            <MDBContainer>
                <MDBRow style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                }}>
                    <h1>Manageing a single store here - adding managers and owners, editing products and discounts</h1>
                </MDBRow>
            </MDBContainer>
        );
    }
}

export default SingleStoreManagePage;